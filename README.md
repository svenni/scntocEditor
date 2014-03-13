scntocEditor
============

A python module / PyQt gui to handle modifying Softimage scntoc files.

The first part is the scntoc module itself which handles parsing and modifying
scntoc files on the low level. At the time of writing this scntocEditor only
handles the reference models (since that is what I need right now). This might
get some documentation at some point, until then there are the tests as well
as this tiny example:

    st = scntoc.SCNTOC.from_file('path/to/file.scntoc')

    for model in st.models():
        print 'model name:', model.name()
        print 'model active resolution name:', model.active_resolution().name()
        for resolution in model.resolutions():
            print 'resolution name:', resolution.name()
            print 'resolution path:', resolution.path()
    
    st.models()[0].set_active_resolution_id(0)
    st.write()


The other part is the gui (which is EXTREMELY bare bones at the moment) but
that is something that could be opened in Softimage using the onBeginSceneOpenEvent
or some other time.

There are like a thousand things that could be added to it, but only time will
tell how much will actually get put in.