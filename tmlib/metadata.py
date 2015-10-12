from abc import ABCMeta
from abc import abstractmethod
from .errors import MetadataError


class ImageMetadata(object):

    '''
    Abstract base class for image metadata, such as the name of the channel or
    the relative position of the image within the acquisition grid.
    '''

    __metaclass__ = ABCMeta

    BASIC = {
        'id', 'name', 'plane_id', 'time_id',
        'orig_dtype', 'orig_dimensions'
    }

    POSITIONAL = {'site_id'}

    PERSISTENT = BASIC.union(POSITIONAL)

    def __init__(self):
        '''
        Initialize an instance of class ImageMetadata.
        '''
        self.is_aligned = False
        self.is_corrected = False
        self.is_omitted = False

    # TODO: Unfortunately, "PhysicalSize" attributes are not implemented
    # in python-bioformats

    # @property
    # def physical_dimensions(self):
    #     '''
    #     Returns
    #     -------
    #     int
    #         y, x dimensions of the image in micrometer
    #     '''
    #     return self._physical_dimensions

    # @physical_dimensions.setter
    # def physical_dimensions(self, value):
    #     self._physical_dimensions = value

    @property
    def id(self):
        '''
        Returns
        -------
        int
            zero-based unique image identifier number
        '''
        return self._id

    @id.setter
    def id(self, value):
        if not(isinstance(value, int)):
            raise TypeError('Attribute "id" must have type int')
        self._id = value

    @property
    def name(self):
        '''
        Returns
        -------
        str
            name of the image
        '''
        return self._name

    @name.setter
    def name(self, value):
        if not(isinstance(value, basestring)) and value is not None:
            raise TypeError('Attribute "name" must have type basestring')
        self._name = value

    @property
    def site(self):
        '''
        Returns
        -------
        ImageAcquisitionSite
            information about the position of the image within the
            image acquisition grid
        '''
        return self._site

    @site.setter
    def site(self, value):
        if not(isinstance(value, ImageAcquisitionSite)):
            raise TypeError('Attribute "site" must have type ImageAcquisitionSite')
        self._site = value

    # @property
    # def stage_position(self):
    #     '''
    #     Returns
    #     -------
    #     Tuple[float]
    #         absolute y, x microscope stage positions
    #     '''
    #     return self._stage_position

    # @stage_position.setter
    # def stage_position(self, value):
    #     if isinstance(value, list) and len(value) == 2:
    #         value = tuple(value)
    #     if not(isinstance(value, tuple)) and value is not None:
    #         raise TypeError('Attribute "stage_position" must have type tuple')
    #     self._stage_position = value

    @property
    def plane_id(self):
        '''
        Returns
        -------
        int
            zero-based z index of the focal plane within a three dimensional
            stack
        '''
        return self._plane_id

    @plane_id.setter
    def plane_id(self, value):
        if not(isinstance(value, int)) and value is not None:
            raise TypeError('Attribute "plane_id" must have type int')
        self._plane_id = value

    @property
    def time_id(self):
        '''
        Returns
        -------
        int
            one-based time point identifier number
        '''
        return self._time_id

    @time_id.setter
    def time_id(self, value):
        if not(isinstance(value, int)) and value is not None:
            raise TypeError('Attribute "time_id" must have type int')
        self._time_id = value

    @property
    def is_omitted(self):
        '''
        Returns
        -------
        bool
            whether the image should be omitted from further analysis
            (for example because the shift exceeds the maximally tolerated
             shift or the image contains artifacts that would cause problems
             for image analysis algorithms)
        '''
        return self._is_omitted

    @is_omitted.setter
    def is_omitted(self, value):
        if not isinstance(value, bool):
            raise TypeError('Attribute "omit" must have type bool')
        self._is_omitted = value

    @property
    def is_aligned(self):
        '''
        Returns
        -------
        bool
            indicates whether the image has been aligned
        '''
        return self._is_aligned

    @is_aligned.setter
    def is_aligned(self, value):
        if not isinstance(value, bool):
            raise TypeError('Attribute "is_aligned" must have type bool')
        self._is_aligned = value

    @property
    def orig_dtype(self):
        '''
        Returns
        -------
        str
            original image data type as stored by the microscope
        '''
        return self._orig_dtype

    @orig_dtype.setter
    def orig_dtype(self, value):
        if not(isinstance(value, basestring)) and value is not None:
            raise TypeError('Attribute "orig_dtype" must have type basestring')
        self._orig_dtype = value

    @property
    def orig_dimensions(self):
        '''
        Returns
        -------
        str
            original image dimensions as stored by the microscope
        '''
        return self._orig_dimensions

    @orig_dimensions.setter
    def orig_dimensions(self, value):
        if isinstance(value, list) and len(value) == 2:
            value = tuple(value)
        if not(isinstance(value, tuple)) and value is not None:
            raise TypeError('Attribute "orig_dimensions" must have type tuple')
        self._orig_dimensions = value

    @abstractmethod
    def serialize(self):
        '''
        Serialize required metadata attributes to key-value pairs.
        '''
        pass

    @abstractmethod
    def set(metadata):
        '''
        Set attributes from key-value pairs in dictionary.
        '''
        pass


class ChannelImageMetadata(ImageMetadata):

    '''
    Class for metadata specific to channel images.
    '''

    PERSISTENT = ImageMetadata.PERSISTENT.union({
        'channel_name', 'is_corrected', 'is_projected', 'channel_id'
    })

    def __init__(self):
        '''
        Initialize an instance of class ChannelImageMetadata.

        Parameters
        ----------
        metadata: Dict[str, int or str]
            image metadata read from the *.metadata* JSON file
        '''
        super(ChannelImageMetadata, self).__init__()
        self.is_corrected = False
        self.is_projected = False

    @property
    def channel_name(self):
        '''
        Returns
        -------
        str
            name given to the channel
        '''
        return self._channel_name

    @channel_name.setter
    def channel_name(self, value):
        if not(isinstance(value, basestring)) and value is not None:
            raise TypeError('Attribute "channel_name" must have type basestring')
        self._channel_name = value

    @property
    def channel_id(self):
        '''
        Returns
        -------
        int
            zero-based channel identifier number
        '''
        return self._channel_id

    @channel_id.setter
    def channel_id(self, value):
        if not(isinstance(value, int)) and value is not None:
            raise TypeError('Attribute "channel_id" must have type int')
        self._channel_id = value

    @property
    def is_corrected(self):
        '''
        Returns
        -------
        bool
            in case the image is illumination corrected
        '''
        return self._is_corrected

    @is_corrected.setter
    def is_corrected(self, value):
        if not isinstance(value, bool):
            raise TypeError('Attribute "is_corrected" must have type bool')
        self._is_corrected = value

    @property
    def is_projected(self):
        '''
        Returns
        -------
        bool
            in case the image is a 2D projection of a z-stack, i.e.
            a collection of multiple focal planes with the same `channel_id`
            and `time_id`
        '''
        return self._is_projected

    @is_projected.setter
    def is_projected(self, value):
        if not(isinstance(value, bool)):
            raise TypeError('Attribute "is_projected" must have type bool')
        self._is_projected = value

    def __iter__(self):
        '''
        Convert the object to a dictionary.

        Returns
        -------
        dict
            image metadata as key-value pairs

        Raises
        ------
        AttributeError
            when instance doesn't have a required attribute
        '''
        for attr in dir(self):
            if attr in ChannelImageMetadata.PERSISTENT:
                yield (attr, getattr(self, attr))

    @staticmethod
    def set(metadata):
        '''
        Set attributes based on key-value pairs in dictionary.

        Parameters
        ----------
        metadata: dict
            metadata as key-value pairs

        Returns
        -------
        ChannelImageMetadata
            metadata object with `PERSISTENT` attributes set
        '''
        obj = ChannelImageMetadata()
        for key, value in metadata.iteritems():
            if key in ChannelImageMetadata.PERSISTENT:
                setattr(obj, key, value)
        return obj


class ImageFileMapper(object):

    '''
    Container for information about the location of individual images (planes)
    within the original image file and references to the files in which they
    will be stored upon extraction.
    '''

    PERSISTENT = {
        'files', 'series', 'planes',
        'ref_index', 'ref_file', 'ref_id'
    }

    @property
    def files(self):
        '''
        Returns
        -------
        str
            absolute path to the required original image files
        '''
        return self._files

    @files.setter
    def files(self, value):
        if not isinstance(value, list):
            raise TypeError('Attribute "files" must have type list')
        if not all([isinstance(v, basestring) for v in value]):
            raise TypeError('Elements of "files" must have type basestring')
        self._files = value

    @property
    def series(self):
        '''
        Returns
        -------
        int
            zero-based position index of the required series in the original
            file
        '''
        return self._series

    @series.setter
    def series(self, value):
        if not isinstance(value, list):
            raise TypeError('Attribute "series" must have type list')
        if not all([isinstance(v, int) for v in value]):
            raise TypeError('Elements of "series" must have type int')
        self._series = value

    @property
    def planes(self):
        '''
        Returns
        -------
        int
            zero-based position index of the required planes in the original
            file
        '''
        return self._planes

    @planes.setter
    def planes(self, value):
        if not isinstance(value, list):
            raise TypeError('Attribute "planes" must have type list')
        if not all([isinstance(v, int) for v in value]):
            raise TypeError('Elements of "planes" must have type int')
        self._planes = value

    @property
    def ref_index(self):
        '''
        Returns
        -------
        List[str]
            index of the image in the image *Series* in the OMEXML
        '''
        return self._ref_index

    @ref_index.setter
    def ref_index(self, value):
        if not isinstance(value, int):
            raise TypeError('Attribute "ref_index" must have type int')
        self._ref_index = value

    @property
    def ref_id(self):
        '''
        Returns
        -------
        List[str]
            identifier string of the image in the configured OMEXML
            (pattern: (Image:\S+)); e.g. "Image:0")
        '''
        return self._ref_id

    @ref_id.setter
    def ref_id(self, value):
        if not isinstance(value, basestring):
            raise TypeError('Attribute "ref_id" must have type basestring')
        self._ref_id = value

    @property
    def ref_file(self):
        '''
        Returns
        -------
        List[str]
            absolute path to the final image file
        '''
        return self._ref_file

    @ref_file.setter
    def ref_file(self, value):
        if not isinstance(value, basestring):
            raise TypeError('Attribute "ref_file" must have type basestring')
        self._ref_file = value

    def __iter__(self):
        '''
        Returns
        -------
        dict
            key-value representation of the object
            (only `PERSISTENT` attributes)

        Examples
        --------
        >>>obj = ImageFileMapper()
        >>>obj.series = [0, 0]
        >>>obj.planes = [0, 1]
        >>>obj.files = ["a", "b"]
        >>>obj.ref_index = 0
        >>>obj.ref_file = "c"
        >>>obj.ref_id = "Image:0"
        >>>dict(obj)
        {'series': [0, 0], 'planes': [0, 1], 'ref_id': 'Image:0', 'ref_index': 0, 'filenames': ['a', 'b'], 'ref_name': 'c'}
        '''
        for attr in dir(self):
            if attr not in self.PERSISTENT:
                continue
            yield (attr, getattr(self, attr))

    @staticmethod
    def set(description):
        '''
        Parameters
        ----------
        description: dict
            key-value representation of the object

        Returns
        -------
        ImageFileMapper
            object where `PERSISTENT` attributes where set with provided values
        '''
        obj = ImageFileMapper()
        for key, value in description.iteritems():
            if key in obj.PERSISTENT:
                setattr(obj, key, value)
        return obj


# class AcquisitionSiteDescription(object):

#     '''
#     Container for image metadata related to acquisition sites, i.e.
#     row and column positions of the image in the acquisition grid.
#     '''

#     PERSISTENT = {
#         'id', 'image_ids', 'well_id', 'row_index', 'col_index'
#     }

#     @property
#     def id(self):
#         '''
#         Returns
#         -------
#         int
#             zero-based globally unique position identifier number, sorted
#             row-wise over all image acquisition sites

#         Note
#         ----
#         Order of sites is not necessarily according to acquisition time.
#         '''
#         return self._id

#     @id.setter
#     def id(self, value):
#         if not(isinstance(value, int)):
#             raise TypeError('Attribute "site_int" must have type int')
#         self._id = value

#     @property
#     def image_ids(self):
#         '''
#         Returns
#         -------
#         List[int]
#             identifier numbers of images that share the same site
#         '''
#         return self._image_ids

#     @image_ids.setter
#     def image_ids(self, value):
#         if not(isinstance(value, list)):
#             raise TypeError('Attribute "image_ids" must have type list')
#         if not all([isinstance(e, int) for e in value]):
#             raise TypeError('Elements of attribute "image_ids" must have type int')
#         self._image_ids = value

#     @property
#     def row_index(self):
#         '''
#         Returns
#         -------
#         int
#             zero-based row index of the image in the acquisition grid
#         '''
#         return self._row_index

#     @row_index.setter
#     def row_index(self, value):
#         if not(isinstance(value, int)) and value is not None:
#             raise TypeError('Attribute "row_index" must have type int')
#         self._row_index = value

#     @property
#     def col_index(self):
#         '''
#         Returns
#         -------
#         int
#             zero-based column index of the image in the acquisition grid
#         '''
#         return self._col_index

#     @col_index.setter
#     def col_index(self, value):
#         if not(isinstance(value, int)) and value is not None:
#             raise TypeError('Attribute "col_index" must have type int')
#         self._col_index = value

#     @property
#     def grid_coordinates(self):
#         '''
#         Returns
#         -------
#         Tuple[int]
#             zero-based row, column indices of the image in the acquisition grid
#         '''
#         self._coordinates = (self.row_index, self.col_index)
#         return self._coordinates

#     @property
#     def well_id(self):
#         '''
#         Returns
#         -------
#         str
#             well identifier string, e.g. "A01"
#         '''
#         return self._well_id

#     @well_id.setter
#     def well_id(self, value):
#         if not(isinstance(value, basestring)) and value is not None:
#             raise TypeError('Attribute "well_id" must have type str')
#         self._well_id = value

#     def set(self, description):
#         pass

#     def serialize(self):
#         pass


class IllumstatsImageMetadata(object):

    '''
    Class for metadata specific to illumination statistics images.
    '''

    # PERSISTENT = {'channel', 'cycle'}

    def __init__(self):
        '''
        Initialize an instance of class IllumstatsMetadata.
        '''

    @property
    def channel(self):
        '''
        Returns
        -------
        str
            name of the corresponding channel
        '''
        return self._channel

    @channel.setter
    def channel(self, value):
        self._channel = value

    @property
    def cycle(self):
        '''
        Returns
        -------
        str
            name of the corresponding cycle
        '''
        return self._cycle

    @cycle.setter
    def cycle(self, value):
        self._cycle = value

    @property
    def filename(self):
        '''
        Returns
        -------
        str
            name of the statistics file
        '''
        return self._filename

    @filename.setter
    def filename(self, value):
        self._filename = value


class MosaicMetadata(object):

    '''
    Class for mosaic image metadata, such as the name of the channel or
    the relative position of the mosaic within a well plate.
    '''

    @property
    def name(self):
        '''
        Returns
        -------
        str
            name of the corresponding layer
        '''
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def cycle_name(self):
        '''
        Returns
        -------
        str
            name of the corresponding cycle
        '''
        return self._cycle_name

    @cycle_name.setter
    def cycle_name(self, value):
        self._cycle_name = value

    @property
    def channel_name(self):
        '''
        Returns
        -------
        str
            name of the corresponding channel
        '''
        return self._channel_name

    @channel_name.setter
    def channel_name(self, value):
        self._channel_name = value

    @property
    def site_ids(self):
        '''
        Returns
        -------
        List[int]
            site identifier numbers of images contained in the mosaic
        '''
        return self._site_ids

    @site_ids.setter
    def site_ids(self, value):
        self._site_ids = value

    @property
    def filenames(self):
        '''
        Returns
        -------
        List[str]
            names of the individual image files, which make up the mosaic
        '''
        return self._filenames

    @filenames.setter
    def filenames(self, value):
        self._filenames = value

    @staticmethod
    def create_from_images(images, layer_name):
        '''
        Create a MosaicMetadata object from image objects.

        Parameters
        ----------
        images: List[ChannelImage]
            set of images that are all of the same *cycle* and *channel*

        Returns
        -------
        MosaicMetadata

        Raises
        ------
        MetadataError
            when `images` are not of same *cycle* or *channel*
        '''
        cycles = list(set([im.metadata.cycle_name for im in images]))
        if len(cycles) > 1:
            raise MetadataError('All images must be of the same cycle')
        channels = list(set([im.metadata.channel_name for im in images]))
        if len(channels) > 1:
            raise MetadataError('All images must be of the same channel')
        planes = list(set([im.metadata.plane_id for im in images]))
        if len(planes) > 1:
            raise MetadataError('All images must be of the same focal plane')
        metadata = MosaicMetadata()
        metadata.name = layer_name
        metadata.cycle_name = cycles[0]
        metadata.channel_name = channels[0]
        metadata.plane_id = planes[0]
        # sort filenames according to sites
        sites = [im.metadata.site_id for im in images]
        sort_order = [sites.index(s) for s in sorted(sites)]
        metadata.site_ids = sorted(sites)
        files = [im.metadata.name for im in images]
        metadata.filenames = [files[ix] for ix in sort_order]
        return metadata