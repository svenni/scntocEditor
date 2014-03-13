import unittest
import xml.etree.ElementTree as ET

import scntoc

proper_resolution_xml_root = ET.Element('resolution')
proper_resolution_xml_root.set('name', 'ResName')
proper_resolution_xml_root.set('id', '0')
proper_resolution_xml_root.set('href', 'file://path_to_file')


class TestResolution(unittest.TestCase):
    def test_creation(self):
        res = scntoc.Resolution('ResName', 0, 'file://path_to_file')
        self.assertEquals(res.name(), 'ResName')
        self.assertEquals(res.id(), 0)
        self.assertEquals(res.href(), 'file://path_to_file')

    def test_changing_name(self):
        res = scntoc.Resolution('ResName', 0, 'file://path_to_file')
        self.assertEquals(res.name(), 'ResName')
        res.set_name('newName')
        self.assertEquals(res.name(), 'newName')

    def test_changin_id(self):
        res = scntoc.Resolution('ResName', 0, 'file://path_to_file')
        self.assertEquals(res.id(), 0)
        res.setId(4)
        self.assertEquals(res.id(), 4)

    def test_changin_path(self):
        res = scntoc.Resolution('ResName', 0, 'file://path_to_file')
        self.assertEquals(res.href(), 'file://path_to_file')
        res.set_href('file://new_path')
        self.assertEquals(res.href(), 'file://new_path')

    def test_auto_href_prefixing(self):
        res = scntoc.Resolution('ResName', 0, '//server/share/file')
        self.assertEquals(res.href(), 'file:////server/share/file')

    def test_auto_href_prefixing_empty_href(self):
        res = scntoc.Resolution('Offloaded', 0, '')
        self.assertEquals(res.href(), '')

    def test_auto_href_pathdelimfixing(self):
        res = scntoc.Resolution('ResName', 0, r'\\server\share\file')
        self.assertEquals(res.href(), 'file:////server/share/file')

    def test_auto_href_pathdelim_and_prefixing(self):
        res = scntoc.Resolution('ResName', 0, r'file:\\\\server\share\file')
        self.assertEquals(res.href(), 'file:////server/share/file')

    def test_xml_generation(self):
        res = scntoc.Resolution('ResName', 0, 'file://path_to_file')
        xml_element = res.xml()

        self.assertEquals(xml_element.tag, proper_resolution_xml_root.tag)
        self.assertEquals(xml_element.tag, proper_resolution_xml_root.tag)
        self.assertEquals(xml_element.attrib, proper_resolution_xml_root.attrib)
        self.assertEquals(xml_element.tail, proper_resolution_xml_root.tail)

    def test_creation_from_xml_success(self):
        xml_element = ET.Element('resolution')
        xml_element.set('name', 'XMLname')
        xml_element.set('id', 0)
        xml_element.set('href', 'file://server/share/file')

        res = scntoc.Resolution.from_xml(xml_element)
        self.assertTrue(isinstance(res, scntoc.Resolution))
        self.assertEquals(res.name(), 'XMLname')
        self.assertEquals(res.id(), 0)
        self.assertEquals(res.href(), 'file://server/share/file')

    def test_get_path(self):
        res = scntoc.Resolution('ResName', 0, 'file://path_to_file')
        self.assertEquals(res.name(), 'ResName')
        self.assertEquals(res.path(), 'path_to_file')
