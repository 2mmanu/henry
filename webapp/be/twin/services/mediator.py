def mediator(self, ontology: str, question: str) -> str:
    """
    Mediate a complex request to the given API with provided ontology and question, and return the response value.

    :param ontology: The ontology to be used in the API request.
    :type ontology: str
    :param question: The question to be sent to the API.
    :type question: str
    :return: The response from the API as a string.
    :rtype: str
    :raises requests.HTTPError: If the request to the API returns a status code indicating an error.
    :raises requests.RequestException: If there is an error making the request.

    Example usage:
    mediator("HR", "This is Bob's CV, what could be his starting salary?")
    mediator("HR", "I would like to take a day off on July 5th.")

    """
    import requests
    api_url = 'http://fastapi-service-m/api/v1/query'
    params = {'ontology': ontology, 'question': question}

    response = requests.get(api_url, params=params)
    return response.text