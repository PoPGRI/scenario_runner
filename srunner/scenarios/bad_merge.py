#!/usr/bin/env python

# Copyright (c) 2018-2020 Intel Corporation
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

# modified by Shengkun Cui

"""
Ghost Cut In:

The scenario realizes a common driving behavior, in which the
user-controlled ego vehicle follows a lane at constant speed and
an npc suddenly cut into the lane from the left while slowing down.
THe user-controlled ego vechicle should break and stop if necessary
to avoid a crash.
"""

import random

import py_trees

import carla

from srunner.scenariomanager.carla_data_provider import CarlaDataProvider
from srunner.scenariomanager.scenarioatomics.atomic_behaviors import (ActorTransformSetter,
                                                                      ActorDestroy,
                                                                      KeepVelocity,
                                                                      StopVehicle,
                                                                      WaypointFollower,
                                                                      ChangeAutoPilot,
                                                                      LaneChange)
from srunner.scenariomanager.scenarioatomics.atomic_criteria import CollisionTest
from srunner.scenariomanager.scenarioatomics.atomic_trigger_conditions import (InTriggerDistanceToVehicle,
                                                                               InTriggerDistanceToNextIntersection,
                                                                               DriveDistance,
                                                                               StandStill)
from srunner.scenariomanager.timer import TimeOut
from srunner.scenarios.basic_scenario import BasicScenario
from srunner.tools.scenario_helper import get_waypoint_in_distance


class BadMerge(BasicScenario):

    """
    This class holds everything required for a simple "Follow a leading vehicle"
    scenario involving two vehicles.  (Traffic Scenario 2)

    This is a single ego vehicle scenario
    """

    timeout = 120            # Timeout of scenario in seconds

    def __init__(self, world, ego_vehicles, config, randomize=False, debug_mode=False, criteria_enable=True,
                 timeout=60):
        """
        Setup all relevant parameters and create scenario

        If randomize is True, the scenario parameters are randomized
        """

        self._map = CarlaDataProvider.get_map()
        self._first_vehicle_location = 0
        self._first_vehicle_speed = 20
        self._reference_waypoint = self._map.get_waypoint(
            config.trigger_points[0].location)
        self._other_actor_max_brake = 1.0
        self._other_actor_stop_in_front_intersection = 20
        self._other_actor_transform = None
        self.world = world
        self.ego_vehicles = ego_vehicles
        # Timeout of scenario in seconds
        self.timeout = timeout

        super(BadMerge, self).__init__("BadMerge",
                                       ego_vehicles,
                                       config,
                                       world,
                                       debug_mode,
                                       criteria_enable=criteria_enable)

        if randomize:
            self._ego_other_distance_start = random.randint(4, 8)

            # Example code how to randomize start location
            # distance = random.randint(20, 80)
            # new_location, _ = get_location_in_distance(self.ego_vehicles[0], distance)
            # waypoint = CarlaDataProvider.get_map().get_waypoint(new_location)
            # waypoint.transform.location.z += 39
            # self.other_actors[0].set_transform(waypoint.transform)

    def _initialize_actors(self, config):
        """
        Custom initialization
        """

        first_vehicle_waypoint, _ = get_waypoint_in_distance(
            self._reference_waypoint, self._first_vehicle_location)
        # self._other_actor_transform = carla.Transform(
        #     carla.Location(82.58187866210938,
        #                    20.49610137939453,
        #                    0.1),
        #     carla.Rotation(0, 97.6387634277, 0))
        # first_vehicle_transform = carla.Transform(
        #     carla.Location(82.58187866210938,
        #                    20.49610137939453,
        #                    0.1),
        #     self._other_actor_transform.rotation)

        ego_vehicle_waypoint = self.world.get_map().get_waypoint(self.ego_vehicles[0].get_location(), project_to_road=True, lane_type=carla.LaneType.Driving)
        # self._other_actor_transform = carla.Transform(
        #     carla.Location(ego_vehicle_waypoint.next(80)[0].transform.location.x,
        #                    ego_vehicle_waypoint.next(80)[0].transform.location.y,
        #                    0),
        #     ego_vehicle_waypoint.next(80)[0].transform.rotation)
        self._other_actor_transform = ego_vehicle_waypoint.next(80)[0].transform
        # print(self._other_actor_transform)
        first_vehicle_transform = self._other_actor_transform
        first_vehicle = CarlaDataProvider.request_new_actor('vehicle.tesla.model3',
                                                            first_vehicle_transform)
        first_vehicle.set_simulate_physics(enabled=True)
        self.other_actors.append(first_vehicle)

    def _create_behavior(self):
        """
        The scenario defined after is a "follow leading vehicle" scenario. After
        invoking this scenario, it will wait for the user controlled vehicle to
        enter the start region, then make the other actor to drive until reaching
        the next intersection. Finally, the user-controlled vehicle has to be close
        enough to the other actor to end the scenario.
        If this does not happen within 60 seconds, a timeout stops the scenario
        """

        # to avoid the other actor blocking traffic, it was spawed elsewhere
        # reset its pose to the required one
        start_transform = ActorTransformSetter(
            self.other_actors[0], self._other_actor_transform)

        # let the other actor drive and catch up, and perform a dangerous merge lane
        driving_forward_and_change_lane = py_trees.composites.Parallel("Driving forward and chagne lane",
                                                                       policy=py_trees.common.ParallelPolicy.SUCCESS_ON_ALL)

        # start_driving = py_trees.composites.Sequence("Start Driving")
        # start_driving.add_child(InTriggerDistanceToVehicle(self.other_actors[0],
        #                                                                   self.ego_vehicles[0],
        #                                                                   distance=20,
        #                                                                   name="Distance"))
        # start_driving.add_child(ChangeAutoPilot(self.other_actors[0], True,
        #                                                              parameters={"max_speed": self._first_vehicle_speed}))
        # start_driving.add_child(KeepVelocity(self.other_actors[0], self._first_vehicle_speed))

        merge_left = py_trees.composites.Sequence("Drive Straight")
        merge_left.add_child(InTriggerDistanceToVehicle(self.other_actors[0],
                                                        self.ego_vehicles[0],
                                                        distance=10,
                                                        name="Distance"))
        merge_left.add_child(ChangeAutoPilot(self.other_actors[0], True,
                                             parameters={"max_speed": self._first_vehicle_speed}))
        merge_left.add_child(KeepVelocity(
            self.other_actors[0], self._first_vehicle_speed))

        # merge_right = py_trees.composites.Sequence("Merge Lane")
        # merge_right.add_child(InTriggerDistanceToVehicle(self.other_actors[0],
        #                                                                   self.ego_vehicles[0],
        #                                                                   distance=10,
        #                                                                   name="Distance"))
        # merge_right.add_child(LaneChange(self.other_actors[0],
        #                                                          direction="right",
        #                                                          distance_same_lane=0,
        #                                                          distance_other_lane=200,
        #                                                          distance_lane_change=5,
        #                                                          speed=20))

        # construct scenario
        # driving_forward_and_change_lane.add_child(start_driving)
        driving_forward_and_change_lane.add_child(merge_left)
        # driving_forward_and_change_lane.add_child(merge_right)

        # end condition
        endcondition = py_trees.composites.Parallel("Waiting for end position",
                                                    policy=py_trees.common.ParallelPolicy.SUCCESS_ON_ALL)
        endcondition_part = StandStill(
            self.ego_vehicles[0], name="StandStill", duration=15)
        endcondition.add_child(endcondition_part)

        # Build behavior tree
        sequence = py_trees.composites.Sequence("Sequence Behavior")
        sequence.add_child(start_transform)
        sequence.add_child(driving_forward_and_change_lane)
        sequence.add_child(endcondition)
        sequence.add_child(ActorDestroy(self.other_actors[0]))

        return sequence

    def _create_test_criteria(self):
        """
        A list of all test criteria will be created that is later used
        in parallel behavior tree.
        """
        criteria = []

        collision_criterion = CollisionTest(self.ego_vehicles[0])

        criteria.append(collision_criterion)

        return criteria

    def __del__(self):
        """
        Remove all actors upon deletion
        """
        self.remove_all_actors()
