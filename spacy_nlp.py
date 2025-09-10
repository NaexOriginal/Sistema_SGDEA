import spacy

#* Cargar el modelo de spaCy
try:
  nlp = spacy.load("es_core_news_sm")
  
except OSError:
  from spacy.cli import download
  download("es_core_news_sm")
  nlp = spacy.load("es_core_news_sm")
  

def extraer_entidades(texto):
  doc = nlp(texto)
  entidades_encontradas = {}
  
  for ent in doc.ents:
    if ent.label_ == "PER":
      if "PERSONA" not in entidades_encontradas:
        entidades_encontradas["PERSONA"] = []
        
      entidades_encontradas["PERSONA"].append(ent.text)
  
    elif ent.label_ == "LOC":
      if "UBICACION" not in entidades_encontradas:
        entidades_encontradas["UBICACION"] = []
        
      entidades_encontradas["UBICACION"].append(ent.text)
      
    elif ent.label_ == "MISC":
      if "MISC" not in entidades_encontradas:
        entidades_encontradas["MISC"] = []
        
      entidades_encontradas["MISC"].append(ent.text)
      
    elif ent.label_ == "ORG":
      if "ORGANIZACION" not in entidades_encontradas:
        entidades_encontradas["ORGANIZACION"] = []
        
      entidades_encontradas["ORGANIZACION"].append(ent.text)
      
    elif ent.label_ == "DATE":
      if "FECHA" not in entidades_encontradas:
        entidades_encontradas["FECHA"] = []
        
      entidades_encontradas["FECHA"].append(ent.text)
  
  return entidades_encontradas