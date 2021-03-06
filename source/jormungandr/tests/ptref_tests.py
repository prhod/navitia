# encoding: utf-8
# Copyright (c) 2001-2014, Canal TP and/or its affiliates. All rights reserved.
#
# This file is part of Navitia,
#     the software to build cool stuff with public transport.
#
# Hope you'll enjoy and contribute to this project,
#     powered by Canal TP (www.canaltp.fr).
# Help us simplify mobility and open public transport:
#     a non ending quest to the responsive locomotion way of traveling!
#
# LICENCE: This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Stay tuned using
# twitter @navitia
# IRC #navitia on freenode
# https://groups.google.com/d/forum/navitia
# www.navitia.io
import urllib
from tests.check_utils import journey_basic_query
from tests.tests_mechanism import dataset, AbstractTestFixture
from check_utils import *


@dataset(["main_ptref_test"])
class TestPtRef(AbstractTestFixture):
    """
    Test the structure of the ptref response
    """

    def test_vj_default_depth(self):
        """default depth is 1"""
        response = self.query_region("v1/vehicle_journeys")

        vjs = get_not_null(response, 'vehicle_journeys')

        for vj in vjs:
            is_valid_vehicle_journey(vj, depth_check=1)

        assert len(vjs) == 3
        vj = vjs[0]
        assert vj['id'] == 'vj1'

        assert len(vj['stop_times']) == 2
        assert vj['stop_times'][0]['arrival_time'] == '101500'
        assert vj['stop_times'][0]['departure_time'] == '101500'
        assert vj['stop_times'][1]['arrival_time'] == '111000'
        assert vj['stop_times'][1]['departure_time'] == '111000'

        #we added some comments on the vj, we should have them
        com = get_not_null(vj, 'comments')
        assert len(com) == 1
        assert com[0]['type'] == 'standard'
        assert com[0]['value'] == 'hello'
        assert "feed_publishers" in response
        
        feed_publisher = response["feed_publishers"][0]
        is_valid_feed_publisher(feed_publisher)
        assert (feed_publisher["id"] == "builder")
        assert (feed_publisher["name"] == "canal tp")
        assert (feed_publisher["license"] == "ODBL")
        assert (feed_publisher["url"] == "www.canaltp.fr")

    def test_vj_depth_0(self):
        """default depth is 1"""
        response = self.query_region("v1/vehicle_journeys?depth=0")

        vjs = get_not_null(response, 'vehicle_journeys')

        for vj in vjs:
            is_valid_vehicle_journey(vj, depth_check=0)

    def test_vj_depth_2(self):
        """default depth is 1"""
        response = self.query_region("v1/vehicle_journeys?depth=2")

        vjs = get_not_null(response, 'vehicle_journeys')

        for vj in vjs:
            is_valid_vehicle_journey(vj, depth_check=2)

    def test_vj_depth_3(self):
        """default depth is 1"""
        response = self.query_region("v1/vehicle_journeys?depth=3")

        vjs = get_not_null(response, 'vehicle_journeys')

        for vj in vjs:
            is_valid_vehicle_journey(vj, depth_check=3)

    def test_vj_show_codes_propagation(self):
        """stop_area:stop1 has a code, we should be able to find it when accessing it by the vj"""
        response = self.query_region("stop_areas/stop_area:stop1/vehicle_journeys?show_codes=true")

        vjs = get_not_null(response, 'vehicle_journeys')

        assert vjs

        for vj in vjs:
            is_valid_vehicle_journey(vj, depth_check=1)

        stop_points = [get_not_null(st, 'stop_point') for vj in vjs for st in vj['stop_times']]
        stops1 = [s for s in stop_points if s['id'] == 'stop_area:stop1']
        assert stops1

        for stop1 in stops1:
            # all reference to stop1 must have it's codes
            codes = get_not_null(stop1, 'codes')
            code_uic = [c for c in codes if c['type'] == 'code_uic']
            assert len(code_uic) == 1 and code_uic[0]['value'] == 'bobette'

    def test_line(self):
        """test line formating"""
        response = self.query_region("v1/lines")

        lines = get_not_null(response, 'lines')

        assert len(lines) == 3

        l = lines[0]

        is_valid_line(l, depth_check=1)

        assert l["text_color"] == 'FFD700'
        #we know we have a geojson for this test so we can check it
        geo = get_not_null(l, 'geojson')
        shape(geo)

        com = get_not_null(l, 'comments')
        assert len(com) == 1
        assert com[0]['type'] == 'standard'
        assert com[0]['value'] == "I'm a happy comment"

        physical_modes = get_not_null(l, 'physical_modes')
        assert len(physical_modes) == 1

        is_valid_physical_mode(physical_modes[0], depth_check=1)

        assert physical_modes[0]['id'] == 'physical_mode:Car'
        assert physical_modes[0]['name'] == 'name physical_mode:Car'

        line_group = get_not_null(l, 'line_groups')
        assert len(line_group) == 1
        is_valid_line_group(line_group[0], depth_check=0)
        assert line_group[0]['name'] == 'A group'
        assert line_group[0]['id'] == 'group:A'

    def test_line_groups(self):
        """test line group formating"""
        # Test for each possible range to ensure main_line is always at a depth of 0
        for depth in range(0,3):
            response = self.query_region("line_groups?depth={0}".format(depth))

            line_groups = get_not_null(response, 'line_groups')

            assert len(line_groups) == 1

            lg = line_groups[0]

            is_valid_line_group(lg, depth_check=depth)

            if depth > 0:
                com = get_not_null(lg, 'comments')
                assert len(com) == 1
                assert com[0]['type'] == 'standard'
                assert com[0]['value'] == "I'm a happy comment"

        # test if line_groups are accessible through the ptref graph
        response = self.query_region("routes/line:A:0/line_groups")
        line_groups = get_not_null(response, 'line_groups')
        assert len(line_groups) == 1
        lg = line_groups[0]
        is_valid_line_group(lg)

    def test_line_codes(self):
        """test line formating"""
        response = self.query_region("v1/lines/line:A?show_codes=true")

        lines = get_not_null(response, 'lines')

        assert len(lines) == 1

        l = lines[0]

        codes = get_not_null(l, 'codes')

        assert len(codes) == 3

        is_valid_codes(codes)

    def test_route(self):
        """test line formating"""
        response = self.query_region("v1/routes")

        routes = get_not_null(response, 'routes')

        assert len(routes) == 3

        r = [r for r in routes if r['id'] == 'line:A:0']
        assert len(r) == 1
        r = r[0]
        is_valid_route(r, depth_check=1)

        #we know we have a geojson for this test so we can check it
        geo = get_not_null(r, 'geojson')
        shape(geo)

        com = get_not_null(r, 'comments')
        assert len(com) == 1
        assert com[0]['type'] == 'standard'
        assert com[0]['value'] == "I'm a happy comment"

    def test_stop_areas(self):
        """test stop_areas formating"""
        response = self.query_region("v1/stop_areas")

        stops = get_not_null(response, 'stop_areas')

        assert len(stops) == 3

        s = next((s for s in stops if s['name'] == 'stop_area:stop1'))
        is_valid_stop_area(s, depth_check=1)

        com = get_not_null(s, 'comments')
        assert len(com) == 2
        assert com[0]['type'] == 'standard'
        assert com[0]['value'] == "comment on stop A"
        assert com[1]['type'] == 'standard'
        assert com[1]['value'] == "the stop is sad"

    def test_stop_points(self):
        """test stop_areas formating"""
        response = self.query_region("v1/stop_points")

        stops = get_not_null(response, 'stop_points')

        assert len(stops) == 3

        s = next((s for s in stops if s['name'] == 'stop_area:stop2'))
        is_valid_stop_area(s, depth_check=1)

        com = get_not_null(s, 'comments')
        assert len(com) == 1
        assert com[0]['type'] == 'standard'
        assert com[0]['value'] == "hello bob"

    def test_company_default_depth(self):
        """default depth is 1"""
        response = self.query_region("v1/companies")

        companies = get_not_null(response, 'companies')

        for company in companies:
            is_valid_company(company, depth_check=1)

        #we check afterward that we have the right data
        #we know there is only one vj in the dataset
        assert len(companies) == 1
        company = companies[0]
        assert company['id'] == 'CMP1'

    def test_simple_crow_fly(self):
        journey_basic_query = "journeys?from=9;9.001&to=stop_area%3Astop2&datetime=20140105T000000"
        response = self.query_region(journey_basic_query)

        #the response must be still valid (this test the kraken data reloading)
        is_valid_journey_response(response, self.tester, journey_basic_query)

    def test_forbidden_uris_on_line(self):
        """test forbidden uri for lines"""
        response = self.query_region("v1/lines")

        lines = get_not_null(response, 'lines')
        assert len(lines) == 3

        assert len(lines[0]['physical_modes']) == 1
        assert lines[0]['physical_modes'][0]['id'] == 'physical_mode:Car'

        #there is only one line, so when we forbid it's physical mode, we find nothing
        response, code = self.query_no_assert("v1/coverage/main_ptref_test/lines"
                                        "?forbidden_uris[]=physical_mode:Car")
        assert code == 404

        # for retrocompatibility purpose forbidden_id[] is the same
        response, code = self.query_no_assert("v1/coverage/main_ptref_test/lines"
                                        "?forbidden_id[]=physical_mode:Car")
        assert code == 404

        # when we forbid another physical_mode, we find again our line
        response, code = self.query_no_assert("v1/coverage/main_ptref_test/lines"
                                        "?forbidden_uris[]=physical_mode:Bus")
        assert code == 200

    def test_simple_pt_objects(self):
        response = self.query_region('pt_objects?q=stop2')

        is_valid_pt_objects_response(response)

        pt_objs = get_not_null(response, 'pt_objects')
        assert len(pt_objs) == 1

        assert get_not_null(pt_objs[0], 'id') == 'stop_area:stop2'

    def test_query_with_strange_char(self):
        q = 'stop_points/stop_point:stop_with name bob \" , é'
        encoded_q = urllib.quote(q)
        response = self.query_region(encoded_q)

        stops = get_not_null(response, 'stop_points')

        assert len(stops) == 1

        is_valid_stop_point(stops[0], depth_check=1)
        assert stops[0]["id"] == u'stop_point:stop_with name bob \" , é'

    def test_filter_query_with_strange_char(self):
        """test that the ptref mechanism works an object with a weird id"""
        response = self.query_region('stop_points/stop_point:stop_with name bob \" , é/lines')
        lines = get_not_null(response, 'lines')

        assert len(lines) == 1
        for l in lines:
            is_valid_line(l)

    def test_journey_with_strange_char(self):
        #we use an encoded url to be able to check the links
        query = 'journeys?from=stop_with name bob \" , é&to=stop_area:stop1&datetime=20140105T070000'
        response = self.query_region(query, display=True)

        is_valid_journey_response(response, self.tester, urllib.quote_plus(query))

    def test_vj_period_filter(self):
        """with just a since in the middle of the period, we find vj1"""
        response = self.query_region("vehicle_journeys?since=20140105T070000")

        vjs = get_not_null(response, 'vehicle_journeys')
        for vj in vjs:
            is_valid_vehicle_journey(vj, depth_check=1)

        assert 'vj1' in (vj['id'] for vj in vjs)

        # same with an until at the end of the day
        response = self.query_region("vehicle_journeys?since=20140105T000000&until=20140106T0000")
        vjs = get_not_null(response, 'vehicle_journeys')
        assert 'vj1' in (vj['id'] for vj in vjs)

        # there is no vj after the 8
        response, code = self.query_no_assert("v1/coverage/main_ptref_test/vehicle_journeys?since=20140109T070000")

        assert code == 404
        assert get_not_null(response, 'error')['message'] == 'ptref : Filters: Unable to find object'

    def test_line_by_code(self):
        """test the filter=type.has_code(key, value)"""
        response = self.query_region("lines?filter=line.has_code(codeB, B)&show_codes=true")
        lines = get_not_null(response, 'lines')
        assert len(lines) == 1
        assert 'B' in [code['value'] for code in lines[0]['codes'] if code['type'] == 'codeB']


@dataset(["main_ptref_test", "main_routing_test"])
class TestPtRefRoutingAndPtrefCov(AbstractTestFixture):
    def test_external_code(self):
        """test the strange and ugly external code api"""
        response = self.query("v1/lines?external_code=A&show_codes=true")
        lines = get_not_null(response, 'lines')
        assert len(lines) == 1
        assert 'A' in [code['value'] for code in lines[0]['codes'] if code['type'] == 'external_code']

    def test_invalid_url(self):
        """the following bad url was causing internal errors, it should only be a 404"""
        _, status = self.query_no_assert("v1/coverage/lines/bob")
        eq_(status, 404)

@dataset(["main_routing_test"])
class TestPtRefRoutingCov(AbstractTestFixture):

    def test_with_coord(self):
        """test with a coord in the pt call, so a place nearby is actually called"""
        response = self.query_region("coords/{coord}/stop_areas".format(coord=r_coord))

        stops = get_not_null(response, 'stop_areas')

        for s in stops:
            is_valid_stop_area(s)

        #the default is the search for all stops within 200m, so we should have A and C
        eq_(len(stops), 2)

        assert set(["stopA", "stopC"]) == set([s['name'] for s in stops])

    def test_with_coord_distance_different(self):
        """same as test_with_coord, but with 300m radius. so we find all stops"""
        response = self.query_region("coords/{coord}/stop_areas?distance=300".format(coord=r_coord))

        stops = get_not_null(response, 'stop_areas')

        for s in stops:
            is_valid_stop_area(s)

        eq_(len(stops), 3)
        assert set(["stopA", "stopB", "stopC"]) == set([s['name'] for s in stops])

    def test_with_coord_and_filter(self):
        """
        we now test with a more complex query, we want all stops with a metro within 300m of r

        only A and C have a metro line
        Note: the metro is physical_mode:0x1
        """
        response = self.query_region("physical_modes/physical_mode:0x1/coords/{coord}/stop_areas"
                                     "?distance=300".format(coord=r_coord), display=True)

        stops = get_not_null(response, 'stop_areas')

        for s in stops:
            is_valid_stop_area(s)

        #the default is the search for all stops within 200m, so we should have all 3 stops
        #we should have 3 stops
        eq_(len(stops), 2)
        assert set(["stopA", "stopC"]) == set([s['name'] for s in stops])

    def test_all_lines(self):
        """test with all lines in the pt call"""
        response = self.query_region('lines')
        assert 'error' not in response
        lines = get_not_null(response, 'lines')
        eq_(len(lines), 4)
        assert {"1A", "1B", "1C", "1D"} == {l['code'] for l in lines}

    def test_line_filter_line_code(self):
        """test filtering lines from line code 1A in the pt call"""
        response = self.query_region('lines?filter=line.code=1A')
        assert 'error' not in response
        lines = get_not_null(response, 'lines')
        eq_(len(lines), 1)
        assert "1A" == lines[0]['code']

    def test_line_filter_line_code_with_resource_uri(self):
        """test filtering lines from line code 1A in the pt call with a resource uri"""
        response = self.query_region('physical_modes/physical_mode:0x1/lines?filter=line.code=1D')
        assert 'error' not in response
        lines = get_not_null(response, 'lines')
        eq_(len(lines), 1)
        assert "1D" == lines[0]['code']

    def test_line_filter_line_code_empty_response(self):
        """test filtering lines from line code bob in the pt call
        as no line has the code "bob" response returns no object"""
        url = 'v1/coverage/main_routing_test/lines?filter=line.code=bob'
        response, status = self.query_no_assert(url)
        assert status == 400
        assert 'error' in response
        assert 'bad_filter' in response['error']['id']

    def test_line_filter_route_code_ignored(self):
        """test filtering lines from route code bob in the pt call
        as there is no attribute "code" for route, filter is invalid and ignored"""
        response_all_lines = self.query_region('lines')
        all_lines = get_not_null(response_all_lines, 'lines')
        response = self.query_region('lines?filter=route.code=bob')
        assert 'error' not in response
        lines = get_not_null(response, 'lines')
        eq_(len(lines), 4)
        assert {l['code'] for l in all_lines} == {l['code'] for l in lines}

    def test_route_filter_line_code(self):
        """test filtering routes from line code 1B in the pt call"""
        response = self.query_region('routes?filter=line.code=1B')
        assert 'error' not in response
        routes = get_not_null(response, 'routes')
        eq_(len(routes), 1)
        assert "1B" == routes[0]['line']['code']

    def test_headsign(self):
        """test basic usage of headsign"""
        response = self.query_region('vehicle_journeys?headsign=vjA')
        assert 'error' not in response
        vjs = get_not_null(response, 'vehicle_journeys')
        eq_(len(vjs), 1)

    def test_headsign_with_resource_uri(self):
        """test usage of headsign with resource uri"""
        response = self.query_region('physical_modes/physical_mode:0x0/vehicle_journeys'
                                     '?headsign=vjA')
        assert 'error' not in response
        vjs = get_not_null(response, 'vehicle_journeys')
        eq_(len(vjs), 1)

    def test_headsign_with_code_filter_and_resource_uri(self):
        """test usage of headsign with code filter and resource uri"""
        response = self.query_region('physical_modes/physical_mode:0x0/vehicle_journeys'
                                     '?headsign=vjA&filter=line.code=1A')
        assert 'error' not in response
        vjs = get_not_null(response, 'vehicle_journeys')
        eq_(len(vjs), 1)

    def test_multiple_resource_uri_no_final_collection_uri(self):
        """test usage of multiple resource uris with line and physical mode giving result,
        then with multiple resource uris giving no result as nothing matches"""
        response = self.query_region('physical_modes/physical_mode:0x0/lines/A')
        assert 'error' not in response
        lines = get_not_null(response, 'lines')
        eq_(len(lines), 1)
        response = self.query_region('lines/D')
        assert 'error' not in response
        lines = get_not_null(response, 'lines')
        eq_(len(lines), 1)
        response = self.query_region('physical_modes/physical_mode:0x1/lines/D')
        assert 'error' not in response
        lines = get_not_null(response, 'lines')
        eq_(len(lines), 1)

        response, status = self.query_region('physical_modes/physical_mode:0x0/lines/D', False)
        assert status == 404
        assert 'error' in response
        assert 'unknown_object' in response['error']['id']

    def test_multiple_resource_uri_with_final_collection_uri(self):
        """test usage of multiple resource uris with line and physical mode giving result,
        as we match it with a final collection, so the intersection is what we want"""
        response = self.query_region('physical_modes/physical_mode:0x1/lines/D/stop_areas')
        assert 'error' not in response
        stop_areas = get_not_null(response, 'stop_areas')
        eq_(len(stop_areas), 2)
        response = self.query_region('physical_modes/physical_mode:0x0/lines/D/stop_areas')
        assert 'error' not in response
        stop_areas = get_not_null(response, 'stop_areas')
        eq_(len(stop_areas), 1)

    def test_headsign_stop_time_vj(self):
        """test basic print of headsign in stop_times for vj"""
        response = self.query_region('vehicle_journeys?filter=vehicle_journey.name="vjA"')
        assert 'error' not in response
        vjs = get_not_null(response, 'vehicle_journeys')
        eq_(len(vjs), 1)
        eq_(len(vjs[0]['stop_times']), 2)
        eq_(vjs[0]['stop_times'][0]['headsign'], "A00")
        eq_(vjs[0]['stop_times'][1]['headsign'], "vjA")

    def test_headsign_display_info_journeys(self):
        """test basic print of headsign in section for journeys"""
        response = self.query_region('journeys?from=stop_point:stopB&to=stop_point:stopA&datetime=20120615T000000')
        assert 'error' not in response
        journeys = get_not_null(response, 'journeys')
        eq_(len(journeys), 1)
        eq_(len(journeys[0]['sections']), 1)
        eq_(journeys[0]['sections'][0]['display_informations']['headsign'], "A00")

    def test_headsign_display_info_departures(self):
        """test basic print of headsign in display informations for departures"""
        response = self.query_region('stop_points/stop_point:stopB/departures?from_datetime=20120615T000000')
        assert 'error' not in response
        departures = get_not_null(response, 'departures')
        eq_(len(departures), 2)
        assert {"A00", "vehicle_journey 1"} == {d['display_informations']['headsign'] for d in departures}

    def test_headsign_display_info_arrivals(self):
        """test basic print of headsign in display informations for arrivals"""
        response = self.query_region('stop_points/stop_point:stopB/arrivals?from_datetime=20120615T000000')
        assert 'error' not in response
        arrivals = get_not_null(response, 'arrivals')
        eq_(len(arrivals), 1)
        eq_(arrivals[0]['display_informations']['headsign'], "vehicle_journey 2")

    def test_headsign_display_info_route_schedules(self):
        """test basic print of headsign in display informations for route schedules"""
        response = self.query_region('routes/A:0/route_schedules?from_datetime=20120615T000000')
        assert 'error' not in response
        route_schedules = get_not_null(response, 'route_schedules')
        eq_(len(route_schedules), 1)
        eq_(len(route_schedules[0]['table']['headers']), 1)
        display_info = route_schedules[0]['table']['headers'][0]['display_informations']
        eq_(display_info['headsign'], "vjA")
        assert {"A00", "vjA"} == set(display_info['headsigns'])

    def test_trip_id_vj(self):
        """test basic print of trip and its id in vehicle_journeys"""
        response = self.query_region('vehicle_journeys')
        assert 'error' not in response
        vjs = get_not_null(response, 'vehicle_journeys')
        for vj in vjs:
            is_valid_vehicle_journey(vj, depth_check=1)
        assert any(vj['name'] == "vehicle_journey 1" and vj['trip']['id'] == "vehicle_journey 1" for vj in vjs)

    def test_disruptions(self):
        """test the /disruptions api"""
        response = self.query_region('disruptions')

        disruptions = get_not_null(response, 'disruptions')
        assert len(disruptions) == 9
        for d in disruptions:
            is_valid_disruption(d)

        # we test that we can access a specific disruption
        response = self.query_region('disruptions/too_bad_line_C')
        disruptions = get_not_null(response, 'disruptions')
        assert len(disruptions) == 1

        # we can also display all disruptions of an object
        response = self.query_region('lines/C/disruptions')
        disruptions = get_not_null(response, 'disruptions')
        assert len(disruptions) == 2
        disruptions_uris = set([d['uri'] for d in disruptions])
        eq_({"too_bad_line_C", "too_bad_all_lines"}, disruptions_uris)

        # we can't access object from the disruption though (we don't think it to be useful for the moment)
        response, status = self.query_region('disruptions/too_bad_line_C/lines', check=False)
        eq_(status, 404)
        e = get_not_null(response, 'error')
        assert e['id'] == 'unknown_object'
        assert e['message'] == 'ptref : Filters: Unable to find object'
