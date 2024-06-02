import cohere
from exa_py import Exa

def makeMap(query):
    co = cohere.Client(api_key=open("COHERE_API_KEY","r").read().replace("\n","").replace(" ",""))

    prompt = open("basePrompt.txt","r").read().replace("{prompt}",query)


    exa = Exa(api_key= open("EXA_API_KEY","r").read().replace("\n","").replace(" ",""))

    results = exa.search_and_contents(
        prompt,
        type="neural",
        use_autoprompt=True,
        num_results=10,
        highlights={
            "num_sentences": 3,
            "highlights_per_url": 10
          }
    )

    ExaContext = []

    for result in results.results:
        for highlight in result.highlights:
            if highlight!="":
                ExaContext.append({
                    "role": "SYSTEM",
                    "message": highlight
                })

    response = co.chat(
        model="command-r-plus",
        chat_history=ExaContext,
        message=prompt
    )

    output = response.text.split("\n")

    concepts = []
    connections = []
    doneConcepts = False

    for line in output:
        if line != "" and line[:5]!="note:" and line[:5] != "Note:" and ":" in line:
            if "->" in line:
                doneConcepts = True
            if line == "<END CONCEPTS>":
                doneConcepts = True
            elif not line in ["<BEGIN CONCEPTS>","<END CONCEPTS>","<BEGIN CONNECTIONS>","<END CONNECTIONS>"]:
                if doneConcepts:
                    connectionDescription = line.split(":")[1]
                    concept1 = line.split(":")[0].split("->")[0]
                    concept2 = line.split(":")[0].split("->")[1]
    
                    while concept1[0] == " ":
                        concept1 = concept1[1:]
                    while concept1[-1] == " ":
                        concept1 = concept1[:-1]
                    while concept2[0] == " ":
                        concept2 = concept2[1:]
                    while concept2[-1] == " ":
                        concept2 = concept2[:-1]
                    while connectionDescription[0] == " ":
                        connectionDescription = connectionDescription[1:]
                    while connectionDescription[-1] == " ":
                        connectionDescription = connectionDescription[:-1]
                    if concept1 in [x[0] for x in concepts] and concept2 in [x[0] for x in concepts]: 
                        connections.append([concept1,concept2,connectionDescription])
                else:
                    description = line.split(":")[1]
                    concept = line.split(":")[0]
    
                    while concept[0] == " ":
                        concept = concept[1:]
                    while concept[-1] == " ":
                        concept = concept[:-1]
                    while len(description)>0 and description[0] == " ":
                        description = description[1:]
                    while len(description)>0 and description[-1] == " ":
                        description = description[:-1]
    
                    concepts.append([concept,description])




    return concepts,connections

#import graphviz

#dot = graphviz.Digraph(comment = query)

#output = "classDiagram\n"

#for concept in concepts:
#    output += concept[0]+" : " + concept[1] + "\n"
    
#    dot.node(concept[0], f"{concept[0]}:\n\n{concept[1]}")

#for connection in connections:
#    output += connection[1] + " <|-- " + connection[0] + " : " + connection[2] + "\n"
#    dot.edge(connection[0],connection[1], label=connection[2])

#dot.render("out.gv",view=True)

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/mindmap', methods=['POST'])
def mindmap():
    data = request.get_json()
    query = data.get('query')

    if not query:
        return jsonify({'error': 'No query provided in the request payload'}), 400

    concepts,connections = makeMap(query)
    result = {"concepts": concepts, "connections": connections}
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=31263)


