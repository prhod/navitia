/* Copyright © 2001-2015, Canal TP and/or its affiliates. All rights reserved.

This file is part of Navitia,
    the software to build cool stuff with public transport.

Hope you'll enjoy and contribute to this project,
    powered by Canal TP (www.canaltp.fr).
Help us simplify mobility and open public transport:
    a non ending quest to the responsive locomotion way of traveling!

LICENCE: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

Stay tuned using
twitter @navitia
IRC #navitia on freenode
https://groups.google.com/d/forum/navitia
www.navitia.io
*/

#define BOOST_TEST_DYN_LINK
#define BOOST_TEST_MODULE test_raptor
#include <boost/test/unit_test.hpp>
#include "routing/raptor.h"
#include "routing/routing.h"
#include "ed/build_helper.h"
#include "tests/utils_test.h"


struct logger_initialized {
    logger_initialized() { init_logger(); }
};
BOOST_GLOBAL_FIXTURE( logger_initialized )

using namespace navitia;
using namespace routing;
namespace bt = boost::posix_time;


BOOST_AUTO_TEST_CASE(freq_vj) {
    ed::builder b("20120614");
    b.frequency_vj("A1", "8:00"_t, "18:00"_t, "00:05"_t)("stop1", "8:00"_t)("stop2", "8:10"_t);

    b.data->pt_data->index();
    b.finish();
    b.data->build_raptor();
    b.data->build_uri();
    RAPTOR raptor(*(b.data));
    const type::PT_Data& d = *b.data->pt_data;

    auto res1 = raptor.compute(d.stop_areas_map.at("stop1"), d.stop_areas_map.at("stop2"), 8*3600, 0, DateTimeUtils::inf, type::RTLevel::Base, true);

    BOOST_REQUIRE_EQUAL(res1.size(), 1);

    BOOST_CHECK_EQUAL(res1[0].items[0].arrival.time_of_day().total_seconds(), 8*3600 + 10*60);

    res1 = raptor.compute(d.stop_areas_map.at("stop1"), d.stop_areas_map.at("stop2"), 9*3600, 0, DateTimeUtils::inf, type::RTLevel::Base, true);
    BOOST_REQUIRE_EQUAL(res1.size(), 1);
    BOOST_CHECK_EQUAL(res1[0].items[0].arrival.time_of_day().total_seconds(), 9*3600 + 10*60);
}


BOOST_AUTO_TEST_CASE(freq_vj_pam) {
    ed::builder b("20120614");
    b.frequency_vj("A1", 8*3600,26*3600,5*60)("stop1", 8*3600)("stop2", 8*3600+10*60);

    b.data->pt_data->index();
    b.finish();
    b.data->build_raptor();
    b.data->build_uri();
    RAPTOR raptor(*(b.data));
    const type::PT_Data& d = *b.data->pt_data;

    auto res1 = raptor.compute(d.stop_areas_map.at("stop1"), d.stop_areas_map.at("stop2"), 23*3600, 0, DateTimeUtils::inf, type::RTLevel::Base, true);

    BOOST_REQUIRE_EQUAL(res1.size(), 1);
    BOOST_CHECK_EQUAL(res1[0].items[0].arrival.time_of_day().total_seconds(), 23*3600 + 10*60);

    /*auto*/ res1 = raptor.compute(d.stop_areas_map.at("stop1"), d.stop_areas_map.at("stop2"), 24*3600, 0, DateTimeUtils::inf, type::RTLevel::Base, true);

    BOOST_REQUIRE_EQUAL(res1.size(), 1);
    BOOST_CHECK_EQUAL(DateTimeUtils::date(to_datetime(res1[0].items[0].arrival, *(b.data))), 1);
    BOOST_CHECK_EQUAL(res1[0].items[0].arrival.time_of_day().total_seconds(), (24*3600 + 10*60)% DateTimeUtils::SECONDS_PER_DAY);

    /*auto*/ res1 = raptor.compute(d.stop_areas_map.at("stop1"), d.stop_areas_map.at("stop2"), 25*3600, 0, DateTimeUtils::inf, type::RTLevel::Base, true);

    BOOST_REQUIRE_EQUAL(res1.size(), 1);
    BOOST_CHECK_EQUAL(DateTimeUtils::date(to_datetime(res1[0].items[0].arrival, *(b.data))), 1);
    BOOST_CHECK_EQUAL(res1[0].items[0].arrival.time_of_day().total_seconds(), (25*3600 + 10*60)% DateTimeUtils::SECONDS_PER_DAY);
}

BOOST_AUTO_TEST_CASE(freq_vj_stop_times) {
    ed::builder b("20120614");
    b.frequency_vj("A1", 8*3600, 18*3600, 60*60)
            ("stop1", 8*3600, 8*3600 + 10*60)
            ("stop2", 8*3600 + 15*60, 8*3600 + 25*60)
            ("stop3", 8*3600 + 30*60, 8*3600 + 40*60);

    b.data->pt_data->index();
    b.finish();
    b.data->build_raptor();
    b.data->build_uri();
    RAPTOR raptor(*(b.data));
    const type::PT_Data& d = *b.data->pt_data;

    const auto check_journey = [](const Path& p) {
        const auto& section = p.items[0];
        BOOST_CHECK_EQUAL(section.departure.time_of_day().total_seconds(), 9*3600 + 10*60);
        BOOST_CHECK_EQUAL(section.arrival.time_of_day().total_seconds(), 9*3600 + 30*60);
        BOOST_REQUIRE_EQUAL(section.stop_times.size(), 3);
        BOOST_REQUIRE_EQUAL(section.departures.size(), 3);
        BOOST_REQUIRE_EQUAL(section.arrivals.size(), 3);
        BOOST_CHECK_EQUAL(section.arrivals[0], "20120614T090000"_dt);
        BOOST_CHECK_EQUAL(section.departures[0], "20120614T091000"_dt);
        BOOST_CHECK_EQUAL(section.arrivals[1], "20120614T091500"_dt);
        BOOST_CHECK_EQUAL(section.departures[1], "20120614T092500"_dt);
        BOOST_CHECK_EQUAL(section.arrivals[2], "20120614T093000"_dt);
        BOOST_CHECK_EQUAL(section.departures[2], "20120614T094000"_dt);
    };

    auto res_earliest = raptor.compute(d.stop_areas_map.at("stop1"), d.stop_areas_map.at("stop3"), 9*3600, 0, DateTimeUtils::inf, type::RTLevel::Base, true);

    BOOST_REQUIRE_EQUAL(res_earliest.size(), 1);
    check_journey(res_earliest[0]);

    //same but tardiest departure
    auto res_tardiest = raptor.compute(d.stop_areas_map.at("stop1"), d.stop_areas_map.at("stop3"), 9*3600 + 30*60, 0, DateTimeUtils::min, type::RTLevel::Base, false);

    BOOST_REQUIRE_EQUAL(res_tardiest.size(), 1);
    check_journey(res_tardiest[0]);
}

/*
 * Test simple frequency trip with different stops duration
 */
BOOST_AUTO_TEST_CASE(freq_vj_different_departure_arrival_duration) {
    // we want to test that everything is fine for a frequency vj
    // with different duration in each stops
    ed::builder b("20120614");
    b.frequency_vj("A1", 8*3600, 18*3600, 60*60)
            ("stop1", 8*3600, 8*3600 + 10*60) //10min
            ("stop2", 8*3600 + 15*60, 8*3600 + 40*60) // 25mn
            ("stop3", 9*3600, 9*3600 + 5*60); //5mn

    b.data->pt_data->index();
    b.finish();
    b.data->build_raptor();
    b.data->build_uri();
    RAPTOR raptor(*(b.data));
    const type::PT_Data& d = *b.data->pt_data;

    const auto check_journey = [](const Path& p) {
        const auto& section = p.items[0];
        BOOST_CHECK_EQUAL(section.departure.time_of_day().total_seconds(), 9*3600 + 10*60);
        BOOST_CHECK_EQUAL(section.arrival.time_of_day().total_seconds(), 10*3600);
        BOOST_REQUIRE_EQUAL(section.stop_times.size(), 3);
        BOOST_REQUIRE_EQUAL(section.departures.size(), 3);
        BOOST_REQUIRE_EQUAL(section.arrivals.size(), 3);
        BOOST_CHECK_EQUAL(section.arrivals[0], "20120614T090000"_dt);
        BOOST_CHECK_EQUAL(section.departures[0], "20120614T091000"_dt);
        BOOST_CHECK_EQUAL(section.arrivals[1], "20120614T091500"_dt);
        BOOST_CHECK_EQUAL(section.departures[1], "20120614T094000"_dt);
        BOOST_CHECK_EQUAL(section.arrivals[2], "20120614T100000"_dt);
        BOOST_CHECK_EQUAL(section.departures[2], "20120614T100500"_dt);
    };

    auto res_earliest = raptor.compute(d.stop_areas_map.at("stop1"), d.stop_areas_map.at("stop3"), 9*3600 + 5*60, 0, DateTimeUtils::inf, type::RTLevel::Base, true);

    BOOST_REQUIRE_EQUAL(res_earliest.size(), 1);
    check_journey(res_earliest[0]);

    //same but tardiest departure
    auto res_tardiest = raptor.compute(d.stop_areas_map.at("stop1"), d.stop_areas_map.at("stop3"), 10*3600, 0, DateTimeUtils::min, type::RTLevel::Base, false);

    BOOST_REQUIRE_EQUAL(res_tardiest.size(), 1);
    check_journey(res_tardiest[0]);
}

/*
 * Test overmidnight cases with different arrival/departure time on the stops
 */
BOOST_AUTO_TEST_CASE(freq_vj_overmidnight_different_dep_arr) {
    ed::builder b("20120612");
    b.frequency_vj("A1", 8*3600, 26*3600, 60*60)
            ("stop1", 8*3600, 8*3600 + 10*60)
            ("stop2", 8*3600 + 30*60, 8*3600 + 35*60)
            ("stop3", 9*3600 + 20*60, 9*3600 + 40*60);

    b.data->pt_data->index();
    b.finish();
    b.data->build_raptor();
    b.data->build_uri();
    RAPTOR raptor(*(b.data));
    const type::PT_Data& d = *b.data->pt_data;

    const auto check_journey = [](const Path& p) {
        const auto& section = p.items[0];
        BOOST_CHECK_EQUAL(section.departure, "20120614T231000"_dt);
        //we arrive at 00:20
        BOOST_CHECK_EQUAL(section.arrival, "20120615T002000"_dt);
        BOOST_REQUIRE_EQUAL(section.stop_times.size(), 3);
        BOOST_REQUIRE_EQUAL(section.departures.size(), 3);
        BOOST_REQUIRE_EQUAL(section.arrivals.size(), 3);
        BOOST_CHECK_EQUAL(section.arrivals[0], "20120614T230000"_dt);
        BOOST_CHECK_EQUAL(section.departures[0], "20120614T231000"_dt);
        BOOST_CHECK_EQUAL(section.arrivals[1], "20120614T233000"_dt);
        BOOST_CHECK_EQUAL(section.departures[1], "20120614T233500"_dt);
        BOOST_CHECK_EQUAL(section.arrivals[2], "20120615T002000"_dt);
        BOOST_CHECK_EQUAL(section.departures[2], "20120615T004000"_dt);
    };

    //leaving at 22:15, we have to wait for the next departure at 23:10
    auto res_earliest = raptor.compute(d.stop_areas_map.at("stop1"), d.stop_areas_map.at("stop3"), 22*3600 + 15*60, 2, DateTimeUtils::inf, type::RTLevel::Base, true);

    BOOST_REQUIRE_EQUAL(res_earliest.size(), 1);
    check_journey(res_earliest[0]);

    //wwe want to arrive before 01:00 we'll take the same trip
    auto res_tardiest = raptor.compute(d.stop_areas_map.at("stop1"), d.stop_areas_map.at("stop3"), 1*3600, 3, DateTimeUtils::min, type::RTLevel::Base, false);

    BOOST_REQUIRE_EQUAL(res_earliest.size(), 1);
    check_journey(res_earliest[0]);
}

BOOST_AUTO_TEST_CASE(freq_vj_transfer_with_regular_vj) {
    ed::builder b("20120614");

    b.frequency_vj("A", "8:00"_t, "26:00"_t, "1:00"_t)
            ("stop1", "8:00"_t, "8:10"_t)
            ("stop2", "8:30"_t, "8:35"_t)
            ("stop3", "9:20"_t, "9:40"_t);

    b.vj("B")("stop4", "12:00"_t, "12:05"_t)
            ("stop2", "12:10"_t, "12:11"_t)
            ("stop5", "12:30"_t, "12:35"_t);

    b.connection("stop2", "stop2", 120);

    b.data->pt_data->index();
    b.finish();
    b.data->build_raptor();
    b.data->build_uri();
    RAPTOR raptor(*(b.data));
    const type::PT_Data& d = *b.data->pt_data;

    const auto check_journey = [](const Path& p) {
        BOOST_REQUIRE_EQUAL(p.items.size(), 3);

        const auto& section = p.items[0];
        //we arrive at 11:30
        BOOST_CHECK_EQUAL(section.departure, "20120616T111000"_dt);
        BOOST_CHECK_EQUAL(section.arrival, "20120616T113000"_dt);
        BOOST_REQUIRE_EQUAL(section.stop_times.size(), 2);
        BOOST_REQUIRE_EQUAL(section.departures.size(), 2);
        BOOST_REQUIRE_EQUAL(section.arrivals.size(), 2);
        BOOST_CHECK_EQUAL(section.arrivals[0], "20120616T110000"_dt);
        BOOST_CHECK_EQUAL(section.departures[0], "20120616T111000"_dt);
        BOOST_CHECK_EQUAL(section.arrivals[1], "20120616T113000"_dt);
        BOOST_CHECK_EQUAL(section.departures[1], "20120616T113500"_dt);

        //waiting section
        const auto& waiting_section = p.items[1];
        BOOST_CHECK_EQUAL(waiting_section.departure, "20120616T113000"_dt);
        BOOST_CHECK_EQUAL(waiting_section.arrival, "20120616T121100"_dt);
        BOOST_REQUIRE_EQUAL(waiting_section.stop_times.size(), 0);
        BOOST_REQUIRE_EQUAL(waiting_section.departures.size(), 0);
        BOOST_REQUIRE_EQUAL(waiting_section.arrivals.size(), 0);

        const auto& second_section = p.items[2];
        BOOST_CHECK_EQUAL(second_section.departure, "20120616T121100"_dt);
        BOOST_CHECK_EQUAL(second_section.arrival, "20120616T123000"_dt);
        BOOST_REQUIRE_EQUAL(second_section.stop_times.size(), 2);
        BOOST_REQUIRE_EQUAL(second_section.departures.size(), 2);
        BOOST_REQUIRE_EQUAL(second_section.arrivals.size(), 2);
        BOOST_CHECK_EQUAL(second_section.arrivals[0], "20120616T121000"_dt);
        BOOST_CHECK_EQUAL(second_section.departures[0], "20120616T121100"_dt);
        BOOST_CHECK_EQUAL(second_section.arrivals[1], "20120616T123000"_dt);
        BOOST_CHECK_EQUAL(second_section.departures[1], "20120616T123500"_dt);
    };

    // leaving after 10:20, we have to wait for the next bus at 11:15
    // then we can catch the bus B at 12:10 and finish at 12:30
    auto res_earliest = raptor.compute(d.stop_areas_map.at("stop1"), d.stop_areas_map.at("stop5"), "10:20"_t, 2, DateTimeUtils::inf, type::RTLevel::Base, true);

    BOOST_REQUIRE_EQUAL(res_earliest.size(), 1);
    check_journey(res_earliest[0]);

    auto res_tardiest = raptor.compute(d.stop_areas_map.at("stop1"), d.stop_areas_map.at("stop5"), "12:40"_t, 2, DateTimeUtils::min, type::RTLevel::Base, false);

    BOOST_REQUIRE_EQUAL(res_tardiest.size(), 1);
    check_journey(res_tardiest[0]);
}

BOOST_AUTO_TEST_CASE(transfer_between_freq) {
    ed::builder b("20120614");

    b.frequency_vj("A", "8:00"_t, "26:00"_t, "1:00"_t)
            ("stop1", "8:00"_t, "8:10"_t)
            ("stop2", "8:30"_t, "8:30"_t)
            ("stop3", "9:20"_t, "9:40"_t);

    b.frequency_vj("B", "14:00"_t, "20:00"_t, "00:10"_t)
            ("stop4", "8:00"_t, "8:14"_t)
            ("stop5", "8:35"_t, "8:44"_t)
            ("stop6", "9:25"_t, "9:34"_t);

    b.connection("stop3", "stop4", "00:20"_t);

    b.data->pt_data->index();
    b.finish();
    b.data->build_raptor();
    b.data->build_uri();
    RAPTOR raptor(*(b.data));
    const type::PT_Data& d = *b.data->pt_data;

    const auto check_journey = [](const Path& p) {
        BOOST_REQUIRE_EQUAL(p.items.size(), 4);

        const auto& section = p.items[0];
        BOOST_CHECK_EQUAL(section.departure, "20120616T121000"_dt);
        BOOST_CHECK_EQUAL(section.arrival, "20120616T132000"_dt);
        BOOST_REQUIRE_EQUAL(section.stop_times.size(), 3);
        BOOST_REQUIRE_EQUAL(section.departures.size(), 3);
        BOOST_REQUIRE_EQUAL(section.arrivals.size(), 3);
        BOOST_CHECK_EQUAL(section.arrivals[0], "20120616T120000"_dt);
        BOOST_CHECK_EQUAL(section.departures[0], "20120616T121000"_dt);
        BOOST_CHECK_EQUAL(section.arrivals[1], "20120616T123000"_dt);
        BOOST_CHECK_EQUAL(section.departures[1], "20120616T123000"_dt);
        BOOST_CHECK_EQUAL(section.arrivals[2], "20120616T132000"_dt);
        BOOST_CHECK_EQUAL(section.departures[2], "20120616T134000"_dt);

        //transfer section
        const auto& transfer_section = p.items[1];
        BOOST_CHECK_EQUAL(transfer_section.departure, "20120616T132000"_dt);
        BOOST_CHECK_EQUAL(transfer_section.arrival, "20120616T134000"_dt);
        BOOST_REQUIRE_EQUAL(transfer_section.stop_times.size(), 0);
        BOOST_REQUIRE_EQUAL(transfer_section.departures.size(), 0);
        BOOST_REQUIRE_EQUAL(transfer_section.arrivals.size(), 0);

        //waiting section
        const auto& waiting_section = p.items[2];
        BOOST_CHECK_EQUAL(waiting_section.departure, "20120616T134000"_dt);
        BOOST_CHECK_EQUAL(waiting_section.arrival, "20120616T141400"_dt);
        BOOST_REQUIRE_EQUAL(waiting_section.stop_times.size(), 0);
        BOOST_REQUIRE_EQUAL(waiting_section.departures.size(), 0);
        BOOST_REQUIRE_EQUAL(waiting_section.arrivals.size(), 0);

        const auto& second_section = p.items[3];
        BOOST_CHECK_EQUAL(second_section.departure, "20120616T141400"_dt);
        BOOST_CHECK_EQUAL(second_section.arrival, "20120616T143500"_dt);
        BOOST_REQUIRE_EQUAL(second_section.stop_times.size(), 2);
        BOOST_REQUIRE_EQUAL(second_section.departures.size(), 2);
        BOOST_REQUIRE_EQUAL(second_section.arrivals.size(), 2);
        BOOST_CHECK_EQUAL(second_section.arrivals[0], "20120616T140000"_dt);
        BOOST_CHECK_EQUAL(second_section.departures[0], "20120616T141400"_dt);
        BOOST_CHECK_EQUAL(second_section.arrivals[1], "20120616T143500"_dt);
        BOOST_CHECK_EQUAL(second_section.departures[1], "20120616T144400"_dt);
    };

    // leaving after 11:10, we would have to wait for the bus B after so the 2nd pass makes us wait
    // so we leave at 12:10 to arrive at 13:20
    // then we have to wait for the begin of the bust B at 14:04 and finish at 14:35
    auto res_earliest = raptor.compute(d.stop_areas_map.at("stop1"), d.stop_areas_map.at("stop5"), "11:10"_t, 2, DateTimeUtils::inf, type::RTLevel::Base, true);

    BOOST_REQUIRE_EQUAL(res_earliest.size(), 1);
    check_journey(res_earliest[0]);

    auto res_tardiest = raptor.compute(d.stop_areas_map.at("stop1"), d.stop_areas_map.at("stop5"), "14:35"_t, 2, DateTimeUtils::min, type::RTLevel::Base, false);

    BOOST_REQUIRE_EQUAL(res_tardiest.size(), 1);
    check_journey(res_tardiest[0]);
}
