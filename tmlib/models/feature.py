# TmLibrary - TissueMAPS library for distibuted image analysis routines.
# Copyright (C) 2016  Markus D. Herrmann, University of Zurich and Robin Hafen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import logging
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref
from sqlalchemy import UniqueConstraint

from tmlib.models.base import ExperimentModel
from tmlib.models.utils import ExperimentConnection
from tmlib import cfg

logger = logging.getLogger(__name__)


class Feature(ExperimentModel):

    '''A *feature* is a measurement that is associated with a particular
    *map object type*. For example a *feature* named "Morphology_Area"
    would correspond to a vector where each value would reflect the area of an
    individual *map object* of a given *map object type*.

    '''

    __tablename__ = 'features'

    __table_args__ = (UniqueConstraint('name', 'mapobject_type_id'), )

    #: str: name given to the feature (e.g. by jterator)
    name = Column(String, index=True)

    #: bool: whether the feature is an aggregate of child object features
    is_aggregate = Column(Boolean, index=True)

    #: int: id of the parent mapobject type
    mapobject_type_id = Column(
        Integer,
        ForeignKey('mapobject_types.id', onupdate='CASCADE', ondelete='CASCADE'),
        index=True
    )

    #: tmlib.models.mapobject.MapobjectType: parent mapobject type
    mapobject_type = relationship(
        'MapobjectType',
        backref=backref('features', cascade='all, delete-orphan')
    )

    def __init__(self, name, mapobject_type_id, is_aggregate=False):
        '''
        Parameters
        ----------
        name: str
            name of the feature
        mapobject_type_id: int
            ID of parent mapobject type
        is_aggregate: bool, optional
            whether the feature is an aggregate calculated based on another
            feature
        '''
        self.name = name
        self.mapobject_type_id = mapobject_type_id
        self.is_aggregate = is_aggregate

    def __repr__(self):
        return '<Feature(id=%r, name=%r)>' % (self.id, self.name)


class FeatureValue(ExperimentModel):

    '''An individual value of a :class:`tmlib.models.feature.Feature`
    that was extracted for a given :class:`tmlib.models.mapobject.Mapobject`
    as part of a :mod:`tmlib.workflow.jterator` pipeline.
    '''

    __tablename__ = 'feature_values'

    __table_args__ = (
        UniqueConstraint('tpoint', 'feature_id', 'mapobject_id'),
    )

    __distribute_by_hash__ = 'mapobject_id'

    #: float: the actual extracted feature value
    value = Column(Float(precision=15))

    #: int: zero-based time point index
    tpoint = Column(Integer, index=True)

    #: int: ID of the parent feature
    feature_id = Column(Integer, index=True, nullable=False)

    #: int: ID of the parent mapobject
    mapobject_id = Column(Integer, index=True, nullable=False)

    def __init__(self, feature_id, mapobject_id, value=None, tpoint=None):
        '''
        Parameters
        ----------
        feature_id: int
            ID of parent feature
        mapobject_id: int
            ID of parent mapobject
        value: float, optional
            actual measurement (default: ``None``)
        tpoint: int, optional
            zero-based time point index (default: ``None``)
        '''
        self.tpoint = tpoint
        self.feature_id = feature_id
        self.mapobject_id = mapobject_id
        self.value = value

    def __repr__(self):
        return (
            '<FeatureValue(id=%d, tpoint=%d, mapobject=%r, feature=%r)>'
            % (self.id, self.tpoint, self.mapobject_id, self.feature_id)
        )


class LabelValue(ExperimentModel):

    '''An individual value of a :class:`tmlib.models.feature.Feature`
    that was assigned to a given :class:`tmlib.models.mapobject.Mapobject`
    as part of a :class:`tmlib.models.result.ToolResult` generated for a client
    tool request.
    '''

    __tablename__ = 'label_values'

    __distribute_by_hash__ = 'mapobject_id'

    #: float: the actual label value
    value = Column(Float(precision=15))

    #: int: zero-based time point index
    tpoint = Column(Integer, index=True)

    #: int: ID of the parent mapobject
    mapobject_id = Column(Integer, index=True, nullable=False)

    #: int: ID of the parent label layer
    tool_result_id = Column(Integer, index=True, nullable=False)

    def __init__(self, tool_result_id, mapobject_id, value=None, tpoint=None):
        '''
        Parameters
        ----------
        tool_result_id: int
            ID of the parent tool result
        mapobject_id: int
            ID of the mapobject to which the value is assigned
        value:
            label value (default: ``None``)
        tpoint: int, optional
            zero-based time point index (default: ``None``)
        '''
        self.tpoint = tpoint
        self.value = value
        self.label_id = label_id
        self.mapobject_id = mapobject_id

    def __repr__(self):
        return (
            '<LabelValue(id=%d, tpoint=%d, mapobject=%r, feature=%r)>'
            % (self.id, self.tpoint, self.mapobject_id, self.feature_id)
        )


def delete_features_cascade(experiment_id, is_aggregate):
    '''Deletes all instances of
    :class:`Feature <tmlib.models.feature.Feature>` as well as
    as "children" instances of
    :class:`FeatureValue <tmlib.models.feature.FeatureValue>`.

    Parameters
    ----------
    experiment_id: int
        ID of the parent :class:`Experiment <tmlib.models.experiment.Experiment>`
    is_aggregate: bool
        whether aggregate or single-object features should be deleted

    Note
    ----
    This is not possible via the standard *SQLAlchemy* approach, because the
    tables of :class:`Mapobject <tmlib.models.mapobject.Mapobject>` and
    :class:`MapobjectSegmentation <tmlib.models.mapobject.MapobjectSegmentation>`
    might be distributed over a cluster.
    '''
    with ExperimentConnection(experiment_id) as connection:
        connection.execute('''
            SELECT id FROM features
            WHERE is_aggregate = %(is_aggregate)s;
        ''', {
            'is_aggregate': is_aggregate
        })
        features = connection.fetchall()
        feature_ids = [f.id for f in features]
        if cfg.db_driver == 'citus':
            logger.info('delete feature values')
            connection.execute('''
                SELECT master_modify_multiple_shards(
                    'DELETE FROM feature_values
                     WHERE feature_id = ANY(%(feature_ids)s)'
                );
            ''', {
                'feature_ids': feature_ids
            })
        else:
            logger.info('delete feature values')
            connection.execute('''
                DELETE FROM feature_values
                WHERE feature_id = ANY(%(feature_ids)s);
            ''', {
                'feature_ids': feature_ids
            })
        connection.execute('''
            DELETE FROM features
            WHERE id = ANY(%(feature_ids)s)
        ''', {
            'feature_ids': feature_ids
        })
