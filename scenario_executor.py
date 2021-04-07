from scenario_runner import ScenarioRunner
from srunner.scenarioconfigs.route_scenario_configuration import RouteScenarioConfiguration
from typing import Dict, List
import carla

class ScenarioArguments:
    def __init__(self, route_config: List[RouteScenarioConfiguration], scenario_config: Dict,
        host = '127.0.0.1', port = '2000', timeout = '10.0', trafficManagerPort = '8000',
        trafficManagerSeed = '0', sync = False, agent = None, agentConfig = '', output = True,
        result_file = False, junit = False, json = False, outputDir = '', configFile = '', 
        additionalScenario = '', debug = False, reloadWorld = False, record = '', 
        randomize = False, repetitions = 1, waitForEgo = False
    ):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.trafficManagerPort = trafficManagerPort
        self.trafficManagerSeed = trafficManagerSeed
        self.sync = sync
        self.agent = agent
        self.agentConfig = agentConfig
        self.output = output
        self.file = result_file
        self.junit = junit
        self.json = json
        self.outputDir = outputDir
        self.configFile = configFile
        self.additionalScenario = additionalScenario
        self.debug = debug
        self.reloadWorld = reloadWorld
        self.record = record
        self.randomize = randomize
        self.repetitions = repetitions
        self.waitForEgo = waitForEgo

        self.route = route_config
        self.scenario_config = scenario_config

class ScenarioExecutor:
    def __init__(self, args: ScenarioArguments):
        self.args = args
        self.scenarios = ScenarioRunner(args)

    def execute(self):
        self.scenarios.run()

if __name__ == "__main__":
    ############### First Scenario ###############
    scenario_config = {
        "t1_triple": [
            {
                "available_event_configurations": [
                    {
                        "transform": {
                            "pitch": "0",
                            "x": "93.1460952758789",
                            "y": "-1.4191741943359375",
                            "yaw": "133.83380126953125",
                            "z": "1.22"
                        }
                    }
                ],
                "scenario_type": "ScenarioBM"
            }
        ]
    }
    
    route_config_list = []
    route_config = RouteScenarioConfiguration()
    route_config.town = 't1_triple'
    route_config.name = 'RouteScenario_0'
    route_config.weather = carla.WeatherParameters(sun_altitude_angle=70)
    route_config.scenario_config = scenario_config
    waypoint_list = []
    waypoint_list.append(carla.Location(
        x=164.0,
        y=-11.0,
        z=0.0
    ))

    waypoint_list.append(carla.Location(
        x=14.7,
        y=69.2,
        z=0.0
    ))

    route_config.trajectory = waypoint_list

    route_config_list.append(route_config)

    args = ScenarioArguments(route_config_list, scenario_config)
    scenario_execution = ScenarioExecutor(args)
    scenario_execution.execute()


    ############### Second Scenario ###############
    scenario_config = {
        "t1_triple": [
            {
                "available_event_configurations": [
                    {
                        "transform": {
                            "pitch": "0",
                            "x": "-85.89",
                            "y": "27.30",
                            "yaw": "-98.2802734375",
                            "z": "1.22"
                        }
                    }
                ],
                "scenario_type": "ScenarioBM"
            }
        ]
    }
    
    route_config_list = []
    route_config = RouteScenarioConfiguration()
    route_config.town = 't1_triple'
    route_config.name = 'RouteScenario_0'
    route_config.weather = carla.WeatherParameters(sun_altitude_angle=70)
    route_config.scenario_config = scenario_config
    waypoint_list = []
    waypoint_list.append(carla.Location(
        x=-23.14,
        y=66.14,
        z=0.0
    ))

    waypoint_list.append(carla.Location(
        x=-74.07,
        y=-90.74,
        z=0.0
    ))

    route_config.trajectory = waypoint_list

    route_config_list.append(route_config)

    args = ScenarioArguments(route_config_list, scenario_config)
    scenario_execution = ScenarioExecutor(args)
    scenario_execution.execute()