import os
import json
import concurrent.futures
from context import ContextAPI
from memgpt import create_client
from memgpt.memory import ChatMemory

class AutoAgent:
    def __init__(self, name:str, context:ContextAPI, agent_role:str, maker:bool):
        self.name = name
        self.context = context
        self.agent_role = agent_role
        self.maker = maker
        self._client = self._get_memgpt_client()
        self._agent_id = self._create_agent(agent_name=self.name,agent_role=self.agent_role)

    def _handle_message(self,messages):
        response = None
        for message in messages.messages:
            if 'internal_monologue' in message:
                print(f"[{self.name}]Internal Monologue:", message['internal_monologue'])
            elif 'function_call' in message:
                try:
                    function_arguments = json.loads(message['function_call']['arguments'])
                    print(f"[{self.name}]Function Call ({message['function_call']['name']}):", function_arguments)
                    if message['function_call']['name'] == 'send_message':
                        response = function_arguments['message']
                except json.JSONDecodeError:
                    print(f"[{self.name}]Function Call:", message['function_call'])
                    if message['function_call']['name'] == 'send_message':
                        response = message['function_call']['arguments']
            elif 'function_return' in message:
                print(f"[{self.name}]Function Return:", message['function_return'])
            else:
                print(f"[{self.name}]Message:", message)
                # TODO warning
                return message
        return response

    def _get_memgpt_client(self):
        return create_client(
            base_url=os.getenv("MEMGPT_BASEURL", default="http://localhost:8083"),
            token= os.getenv("MEMGPT_TOKEN", default="sk-6351c7a8dd436c53e2604799d2ec565cbfba9fba60b3a89a"),
            )
    
    def _create_agent(self,agent_name:str, agent_role:str):

        if not self.maker:
            persona=f"""
            Name: {agent_name}
            Don't ask questions to the user; instead, seek input from other team members about their respective areas.
            {agent_role}
            """
        else:
            persona=f"""
            Name: {agent_name}
            You must create one or more files, seek input from other team members about their respective areas.
            Provide only the code in this format:
            ---filename
            content
            {agent_role}
            """


        chatmemory = ChatMemory(
            human="""
            Name: Mediator
            Agent coordinator
            """, 
            persona=persona
        )
        
        _agent_client = self._client.create_agent(
            memory = chatmemory,
        )

        return _agent_client.id

    def solve(self, problem_description):
        _client = self._get_memgpt_client()
        messages = self.context.get_context()
        response = _client.user_message(agent_id=self._agent_id, message=str(messages))
        response = self._handle_message(response)
        self.context.add_message(agent_name=self.name,message=str(response))

    def review_solution(self, solution, all_solutions):
        _client = self._get_memgpt_client()
        context = self.context.get_context()
        messages = [item for item in context['messages'] if item['agent_name'] != self.name]
        messages = f"Based on everyone’s feedback, try to update and improve your result. {messages}"
        response = _client.user_message(agent_id=self._agent_id, message=str(messages))
        response = self._handle_message(response)
        self.context.add_message(agent_name=self.name,message=str(response))
        

    def finalize_solution(self, all_solutions):
        _client = self._get_memgpt_client()
        message = """
        get your final solution. provide code.
        """
        response = _client.user_message(agent_id=self._agent_id, message=message)
        response = self._handle_message(response)
        self.context.add_message(agent_name=self.name,message=str(response))
        return response


class AgentMediator(AutoAgent):
    def __init__(self,name:str, context:ContextAPI):
        self.applications = []
        self.state = "INITIAL"
        super().__init__(name=name,context=context,agent_role="mediator",maker=False)


    def add_application(self, app):
        print(f"new agent {str(app)}")
        self.applications.append(app)

    def define_problem(self, problem_description:str, create_agents:bool):

        #publish the problem description in the context
        self.problem_description = problem_description
        self.context.add_message(agent_name=self.name,message=self.problem_description)

        if create_agents:
            #create the team 

            _client = self._get_memgpt_client()
            response = _client.user_message(agent_id=self._agent_id, message=f"""
                You are a mediator that coordinates agents.
                We need to: {problem_description}
                As the mediator, you need to identify the necessary team. The team size can range from 1 to 3 agents.
                For each agent, provide the following details: 
                Name: The agent's name (the name must describe the role of agent, eg: backend-dev)
                Long Description: Describe the agent's main responsibilities.
                Flag Maker: A flag that can be either True or False. The flag is True if the agent will create code or text.
                Provide only the output in this format (JSON with a list of dictionaries): 
                {{"agents": [{{"agent_name": "", "long_description": "", "flag_maker": false}}]}}
            """)

            # create the agents 

            self._agents_needed = self._handle_message(response)
            print(self._agents_needed)

            agents = json.loads(self._agents_needed)
            self._agents_needed=agents['agents']
            for agent in self._agents_needed:
                a = AutoAgent(
                    name=agent['agent_name'],
                    context=self.context,
                    agent_role=agent["long_description"],
                    maker=agent["flag_maker"],
                )
                self.add_application(a)

            # create the summiraziton goal and publish it

            response = _client.user_message(agent_id=self._agent_id, message=f"""
                Based on the team created, summarize the composition of the team and their respective goals.
                Remember that the goal is: {problem_description}
            """)
            self._team_goal = self._handle_message(response)
            print(self._team_goal)

            self.context.add_message(agent_name=self.name,message=self._team_goal)
            
        self.state = "PROBLEM_DEFINED"


    def get_solutions(self):
        if self.state != "PROBLEM_DEFINED":
            raise Exception("Problem not defined yet.")
        
        self.solutions = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_app = {executor.submit(app.solve, self.problem_description): app for app in self.applications}
            for future in concurrent.futures.as_completed(future_to_app):
                app = future_to_app[future]
                try:
                    solution = future.result()
                    self.solutions.append((app, solution))
                except Exception as exc:
                    print(f'{app.name} generated an exception: {exc}')
        self.state = "SOLUTIONS_RECEIVED"

    def review_solutions(self, iteration:int):
        if self.state != "SOLUTIONS_RECEIVED":
            raise Exception("Solutions not received yet.")
        for _iteration in range(1,iteration):
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_to_app = {executor.submit(app.review_solution, solution, self.solutions): app for app, solution in self.solutions}
                for future in concurrent.futures.as_completed(future_to_app):
                    app = future_to_app[future]
                    try:
                        future.result()
                    except Exception as exc:
                        print(f'{app.name} generated an exception during review: {exc}')
        self.state = "SOLUTIONS_REVIEWED"

    def finalize_solutions(self):
        if self.state != "SOLUTIONS_REVIEWED":
            raise Exception("Solutions not reviewed yet.")
        
        self.final_solutions = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_app = {executor.submit(app.finalize_solution, self.solutions): app for app in self.applications}
            for future in concurrent.futures.as_completed(future_to_app):
                app = future_to_app[future]
                try:
                    final_solution = future.result()
                    self.final_solutions.append((app, final_solution))
                except Exception as exc:
                    print(f'{app.name} generated an exception during finalization: {exc}')
        self.state = "SOLUTIONS_FINALIZED"

    def get_final_solutions(self):
        if self.state != "SOLUTIONS_FINALIZED":
            raise Exception("Solutions not finalized yet.")
        
        return self.final_solutions



def create_files_from_string(input_string, output_directory='output_files'):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    lines = input_string.splitlines()
    current_filename = None
    file_content = []

    for line in lines:
        if line.startswith('---'):
            if current_filename:
                file_path = os.path.join(output_directory, current_filename)
                with open(file_path, 'w') as output_file:
                    output_file.write(''.join(file_content))
                print(f"create file into {output_directory}/{current_filename}")
                file_content = []
            file_content = []
            current_filename = line.strip()[3:].strip()
        else:
            file_content.append(line + '\n')

    if current_filename:
        file_path = os.path.join(output_directory, current_filename)
        with open(file_path, 'w') as output_file:
            output_file.write(''.join(file_content))
        print(f"create file into {output_directory}/{current_filename}")
    else:
        if file_content:
            default_filename = 'output.txt'
            file_path = os.path.join(output_directory, default_filename)
            with open(file_path, 'w') as output_file:
                output_file.write(''.join(file_content))
            print(f"create file into {output_directory}/{default_filename}")
        else:
            print("No content found to write.")

# Example usage
if __name__ == "__main__":

    # app_name= "demo-creo-login"
    app_name= "demo-challenge"

    context = ContextAPI("http://localhost:8000/v1",context_id=app_name)

    mediator = AgentMediator(name="mediator",context=context)

    #fase 0 fai il recruiment (qui simulato).

    # ci sono due tipi di agenti: designer e maker questo e' esplicitato da descrivi o crea codice
    # i designer sono di supporto alla conoscenza
    # i maker sono agenti che possono produrre un risultato (testo, file) o un'azione con il relativo ritorno

    # app1 = Application("UX-UI-Designer",
    #                    context=context,
    #                    agent_role="""
    #                     This role is responsible for designing the user interface and ensuring an intuitive and pleasant user experience. 
    #                     They focus on the visual appearance of the login page, making sure it is aesthetically pleasing and easy to use.
    #                     your goal is to create a description of the ui.
    #                     """,
    #                     )
    # app2 = Application("Frontend-Developer:",
    #                    context=context,
    #                    agent_role="""
    #                     This professional implements the design of the login page into code using technologies like HTML, CSS, and JavaScript. 
    #                     They handle creating the visible part of the page and making it interactive.
    #                     your goal is only create code.
    #                     """,
    #                    )
    # app3 = Application("Backend-Developer",
    #                    context=context,
    #                    agent_role="""
    #                     This role manages server-side logic, authentication, and security. 
    #                     They connect the login page to the database to verify user credentials and manage sessions.
    #                     your goal is only create code.
    #                     """,
    #                    )

    # mediator.add_application(app1)
    # mediator.add_application(app2)
    # mediator.add_application(app3)

    # problem_description = """
    # We Need to Create a Login Page based on color #258900
    # I need a page index.hml, a style.css and an app.py for the apis with fastapi in python.
    # """

    problem_description = """
    The user needs to interview a candidate for a Junior Software Developer position with a focus on Python. 
    Create a Python application with several exercises. The maximum score achievable is 30 points. 
    Create different levels of difficulty for the exercises. 
    I need a file exercises.py containing the exercises and a file test.py to check if the exercises are solved correctly.
    """

    # fase 1 crea il problema
    mediator.define_problem(problem_description, create_agents=True)

    # fase 2 chiedi una soluzione iniziale agli agenti.
    mediator.get_solutions()

    #fase 3 itera per discutere della soluzione
    mediator.review_solutions(iteration=4)

    #fase 4 realizzativa, i maker devono creare i risultati
    mediator.finalize_solutions()

    #fase 5 gestione del risultato
    final_solutions = mediator.get_final_solutions()

    for app, solution in final_solutions:
        create_files_from_string(solution,output_directory=app_name)

    # fase 6 valutazione human? dipende dai maker cosa possno fare.
    # faccio una sintesi all'umano e gli riepilogo i punti salienti?
