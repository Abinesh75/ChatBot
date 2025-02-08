from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from langchain_community.llms import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate
from langgraph.graph import StateGraph, END
from transformers import pipeline

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin%40123@localhost/chatbot_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    brand = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    contact_info = db.Column(db.String(255), nullable=False)
    product_categories = db.Column(db.String(255), nullable=False)

with app.app_context():
    db.create_all()

hf_pipeline = pipeline("text-generation", model="gpt2")
llm = HuggingFacePipeline(pipeline=hf_pipeline)
prompt = PromptTemplate.from_template("Summarize this: {context}")
chatbot_chain = prompt | llm

def query_database(state):
    query = state["query"].lower().strip()
    session = db.session

    if "products under brand" in query:
        brand = query.split("brand")[-1].strip()
        products = session.query(Product).filter(Product.brand.ilike(brand)).all()
        response = []
        for p in products:
            response.append({"id": p.id, "name": p.name, "price": p.price})
        
        if not response:
            response = "No products found."
        
        return {"query": state["query"], "response": response}

    elif "suppliers provide" in query:
        category = query.split("provide")[-1].strip()
        suppliers = session.query(Supplier).filter(Supplier.product_categories.ilike(f"%{category}%")).all()
        response = []
        for s in suppliers:
            response.append({"id": s.id, "name": s.name})
        
        if not response:
            response = "No suppliers found."
        
        return {"query": state["query"], "response": response}

    elif "details of product" in query:
        product_name = query.split("product")[-1].strip()
        product = session.query(Product).filter(Product.name.ilike(product_name)).first()
        
        if product:
            response = {
                "id": product.id,
                "name": product.name,
                "brand": product.brand,
                "price": product.price,
                "description": product.description or "No description."
            }
        else:
            response = "Product not found."
        
        return {"query": state["query"], "response": response}

    return {"query": state["query"], "response": "I didn't understand your request."}

def enhance_with_llm(state):
    llm_response = chatbot_chain.invoke({"context": state["response"]})
    return {"query": state["query"], "response": llm_response}

graph = StateGraph(dict)
graph.add_node("query_db", query_database)
graph.add_node("llm_response", enhance_with_llm)
graph.set_entry_point("query_db")
graph.add_edge("query_db", "llm_response")
graph.add_edge("llm_response", END)
chat_workflow = graph.compile()

@app.route('/chat', methods=['POST'])
def chat():
    user_query = request.json.get('query', "")
    if not user_query:
        return jsonify({"response": "Query is required."}), 400
    
    state = {"query": user_query, "response": ""}
    result = chat_workflow.invoke(state)  
    return jsonify({"response": result["response"]})  

if __name__ == '__main__':
    app.run(debug=True)