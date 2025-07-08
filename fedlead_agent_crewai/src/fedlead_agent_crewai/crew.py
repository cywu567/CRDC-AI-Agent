from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from fedlead_agent_crewai.tools.login_tool import LoginTool
from fedlead_agent_crewai.tools.navigate_tool import NavigateTool
from fedlead_agent_crewai.tools.find_latest_sr_tool import FindLatestSubmissionTool
from fedlead_agent_crewai.tools.approve_sr_tool import ApproveSRTool
#from fedlead_agent_crewai.tools.create_submission_tool import CreateSubmissionTool
#from fedlead_agent_crewai.tools.smart_fill_form_tool import SmartFillFormTool
from typing import List
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class FedleadAgentCrewai():
    """FedleadAgentCrewai crew"""
    
    agents: List[BaseAgent]
    tasks: List[Task]
    
    def __init__(self, inputs: dict):
        self.inputs = inputs
    
    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def login_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['login_agent'],
            tools=[LoginTool()],
        )
        
    @agent
    def navigate_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['navigate_agent'],
            tools=[NavigateTool()],
        )
        
    @agent
    def find_latest_sr_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['find_latest_sr_agent'],
            tools=[FindLatestSubmissionTool()],
        )
        
    @agent
    def approve_sr_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['approve_sr_agent'],
            tools=[ApproveSRTool()],
        )


    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def login_task(self, inputs=None) -> Task:
        return Task(
            description="Log into the CRDC QA portal using login.gov. Use the login_tool. Credentials are:\n"
                f"Username: {self.inputs['username']}\n"
                f"Password: {self.inputs['password']}\n"
                f"TOTP Secret: {self.inputs['totp_secret']}",
            expected_output="A successful login message or URL verification",
            agent=self.login_agent(),
            input={
                "username": self.inputs["username"],
                "password": self.inputs["password"],
                "totp_secret": self.inputs["totp_secret"]
            },
            input_direct=True,
            args_schema=None
        )
        
    @task
    def navigate_task(self):
        return Task(
            config=self.tasks_config["navigate_task"],
            agent=self.navigate_agent(),
            input={"destination": "submission request"},
            input_direct=True,
        )
        
    @task
    def find_latest_sr_task(self):
        return Task(
            config=self.tasks_config["find_latest_sr_task"],
            agent=self.find_latest_sr_agent(),
            input={"submitter_name": "crdc.cw4"},
            input_direct=True,
        )
    
    @task
    def approve_sr_task(self):
        return Task(
            config=self.tasks_config["approve_sr_task"],
            agent=self.approve_sr_agent(),
        )



    @crew
    def crew(self) -> Crew:
        """Creates the FedleadAgentCrewai crew"""
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            tools=[],
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
