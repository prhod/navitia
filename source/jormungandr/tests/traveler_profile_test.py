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

from jormungandr.travelers_profile import travelers_profile


def test_traveler_profile_override():
    """
     Test traveler profile's factory method make_traveler_profile and override_params
     when overriding args, only non-defined args will be overrided.
    """
    traveler_type = 'standard'
    profile = travelers_profile[traveler_type]

    args = {'walking_speed': 42424242,
            'bike_speed':    42424242}
    profile.override_params(args)

    assert(args['walking_speed'] == 42424242)
    assert(args['bike_speed'] == 42424242)

    arg_vs_profile_attr = (('bss_speed',                  'bss_speed'),
                           ('car_speed',                  'car_speed'),
                           ('max_walking_duration_to_pt', 'max_walking_duration_to_pt'),
                           ('max_bike_duration_to_pt',    'max_bike_duration_to_pt'),
                           ('max_bss_duration_to_pt',     'max_bss_duration_to_pt'),
                           ('max_car_duration_to_pt',     'max_car_duration_to_pt'),
                           ('origin_mode',                'first_section_mode'),
                           ('destination_mode',           'last_section_mode'),
                           ('wheelchair',                 'wheelchair'))

    standard_profile = travelers_profile[traveler_type]

    def check((arg, attr)):
        assert(args[arg] == getattr(standard_profile, attr))

    map(check, arg_vs_profile_attr)