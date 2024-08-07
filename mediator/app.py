import os
import json
import concurrent.futures
from context import ContextAPI
from memgpt import create_client
from memgpt.memory import ChatMemory

class ApplicationMediator:
    def __init__(self,name:str, context:ContextAPI):
        self.name = name
        self.applications = []
        self.state = "INITIAL"
        self.context = context

    def add_application(self, app):
        self.applications.append(app)

    def define_problem(self, problem_description):
        self.problem_description = problem_description
        self.context.add_message(agent_name=self.name,message=self.problem_description)
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




class Application:
    def __init__(self, name:str, context:ContextAPI, agent_role:str):
        self.name = name
        self.context = context
        self.agent_role = agent_role
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
        chatmemory = ChatMemory(
            human="""
            Name: Mediator
            Agent coordinator
            """, 
            persona=f"""
            Name: {agent_name}
            Don't ask questions to the user; instead, seek input from other team members about their respective areas.
            {agent_role}
            """
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


# Example usage
if __name__ == "__main__":

    context = ContextAPI("http://localhost:8000/v1",context_id="demo2")

    mediator = ApplicationMediator(name="mediator",context=context)

    app1 = Application("UX-UI-Designer",
                       context=context,
                       agent_role="""
                        This role is responsible for designing the user interface and ensuring an intuitive and pleasant user experience. 
                        They focus on the visual appearance of the login page, making sure it is aesthetically pleasing and easy to use.
                        your goal is to create a description of the ui.
                        """,
                        )
    app2 = Application("Frontend-Developer:",
                       context=context,
                       agent_role="""
                        This professional implements the design of the login page into code using technologies like HTML, CSS, and JavaScript. 
                        They handle creating the visible part of the page and making it interactive.
                        your goal is only create code.
                        """,
                       )
    app3 = Application("Backend-Developer",
                       context=context,
                       agent_role="""
                        This role manages server-side logic, authentication, and security. 
                        They connect the login page to the database to verify user credentials and manage sessions.
                        your goal is only create code.
                        """,
                       )

    mediator.add_application(app1)
    mediator.add_application(app2)
    mediator.add_application(app3)

    problem_description = """
    We Need to Create a Login Page
    Team Members: UX/UI Designer, Frontend Developer, Backend Developer

    Generate the Design requirements and the Necessary Code

    - UX/UI Designer give a descrption of the page (colors and componets)
    - Backend (Python with FastAPI):
    - Frontend: HTML/CCS/Javascript

    """
    mediator.define_problem(problem_description)

    mediator.get_solutions()
    mediator.review_solutions(iteration=4)
    mediator.finalize_solutions()

    final_solutions = mediator.get_final_solutions()
    for app, solution in final_solutions:
        filename = f"{app.name}.txt"  
        with open(filename, 'w') as file:  
            file.write(solution)
        print(f"File '{filename}' created with solution.")
