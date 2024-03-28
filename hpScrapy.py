import google.generativeai as genai
import textwrap
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from amazoncaptcha import AmazonCaptcha
from IPython.display import Markdown
import json
import csv
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

#arreglos definidos
productosSimilaresArray=[]
linksPPArray=[]
preciosPPArray=[]
tiendasPPArray=[]
estadoPPArray=[]
arregloDicPS=[]
skuArray=[]
nameProductsArray=[]
dicPrincipal=[]
listFInal=[]

def resetearArreglosP():
    global skuArray
    global nameProductsArray
    global dicPrincipal
    global listFInal
    dicPrincipal=[]
    nameProductsArray=[]
    skuArray=[]
    listFInal=[]
    
def resetearArreglos():
    global linksPPArray
    global preciosPPArray
    global tiendasPPArray
    global estadoPPArray
    global arregloDicPS
    global productosSimilaresArray
    productosSimilaresArray=[]
    linksPPArray=[]
    preciosPPArray=[]
    tiendasPPArray=[]
    estadoPPArray=[]
    arregloDicPS=[]

# Configuraciones del webdriver
options = Options()
options.add_experimental_option("detach", True)
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
prefs = {"profile.managed_default_content_settings.images": 2}
options.add_experimental_option("prefs", prefs)

# Crear objeto webdriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

modelo = genai.GenerativeModel('gemini-pro')
GOOGLE_API_KEY='AIzaSyBdrTQrl_xf4qxKn5Oy61wWTfjE67WiRJI'
genai.configure(api_key=GOOGLE_API_KEY)

url_base='https://www.google.com/search?tbm=shop&hl=es-419&psb=1&ved=2ahUKEwix5cLd4ceEAxX4KfYHHQtSAaYQu-kFegQIABAJ&q='

encabezados={
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0 Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
}

def generarLink(producto):
    return url_base + producto.replace(' ', '-')
   
     
def obtenerLinksPP(linkProducto):
    global linksPPArray
    global preciosPPArray
    global tiendasPPArray
    global estadoPPArray
    driver.get(linkProducto)
    linksPP = driver.find_elements(By.XPATH, "//div[@class='mnIHsc']//a[@class='shntl'][1]")
    tiendasPP = driver.find_elements(By.XPATH, "//div[@class='aULzUe IuHnof']")
    preciosPP = driver.find_elements(By.XPATH, "//span[@class='a8Pemb OFFNJ']")
    for i in range(0,3):
     linksPPArray.append(linksPP[i].get_attribute('href'))
    for i in range(0,3):
     preciosPPArray.append(preciosPP[i].text)
    for i in range(0,3):
     tiendasPPArray.append(tiendasPP[i].text)
     
def obtenerLinksPS(nombre,linkProducto):
    global arregloDicPS
    driver.get(linkProducto)
    linksPS = driver.find_elements(By.XPATH, "//div[@class='mnIHsc']//a[@class='shntl'][1]")
    tiendasPS = driver.find_elements(By.XPATH, "//div[@class='aULzUe IuHnof']")
    preciosPS = driver.find_elements(By.XPATH, "//span[@class='a8Pemb OFFNJ']")
    productoSimilarDic = {
            "nombre": nombre,
            "link1": linksPS[0].get_attribute('href'),
            "link2": linksPS[1].get_attribute('href'),
            "link3": linksPS[2].get_attribute('href'),
            "tienda1": tiendasPS[0].text,
            "tienda2": tiendasPS[1].text,
            "tienda3": tiendasPS[2].text,
            "precio1": preciosPS[0].text,
            "precio2": preciosPS[1].text,
            "precio3": preciosPS[2].text
        }
    arregloDicPS.append(productoSimilarDic)

def resolverCaptchaAmazon():
    try:
        # Resolver captcha si es necesario
        captcha_img = driver.find_element(By.XPATH, "//div[@class='a-row a-text-center']//img").get_attribute('src')
        input_field = driver.find_element(By.ID, 'captchacharacters')
        captcha = AmazonCaptcha.fromlink(captcha_img)
        captcha_value = AmazonCaptcha.solve(captcha)
        input_field.send_keys(captcha_value)
        continue_button = driver.find_element(By.CLASS_NAME, 'a-button-text')
        continue_button.click()
    except NoSuchElementException:
        print('No CAPTCHA')

def rebajar(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

def generarPS(producto):
    global productosSimilaresArray
    respuesta = modelo.generate_content("Dame 3 productos similiares a "+producto+' que no sea de la marca, que sean marcas de la competencia. PERO SOLO DAME LOS NOMBRES, NO INFORMACIÓN EXTRA.')
    respuesta = respuesta.text
    respuesta=respuesta.replace('- ', '').replace('* ', '')
    productosSimilaresArray=respuesta.split('\n')
    for i in range(0,3):
        obtenerLinksPS(productosSimilaresArray[i],generarLink(productosSimilaresArray[i]))
        
def leerJSON(file):
  with open(file) as archivo:
    # Cargar los datos desde el archivo JSON
    return json.load(archivo)

    
def agregarInfoDiccionario(sku,preciospp,tiendaspp,linkspp,ps=None):
    global listFInal

    listFInal.append(
            {
               'sku':sku,
               'tienda1':tiendaspp[0],
               'tienda2':tiendaspp[1],
               'tienda3':tiendaspp[2],
               'link1':linkspp[0],
               'link2':linkspp[1],
               'link3':linkspp[2],
               'precio1':preciospp[0],
               'precio2':preciospp[1],
               'precio3':preciospp[2],
               'productosimilar1-name':ps[0]['nombre'],
               'productosimilar2-name':ps[1]['nombre'],
               'productosimilar3-name':ps[2]['nombre'],
               'productosimilar1-link1':ps[0]['link1'],
               'productosimilar1-link2':ps[0]['link2'],
               'productosimilar1-link3':ps[0]['link3'],
               'productosimilar2-link1':ps[1]['link1'],
               'productosimilar2-link2':ps[1]['link2'],
               'productosimilar2-link3':ps[1]['link3'],
               'productosimilar3-link1':ps[2]['link1'],
               'productosimilar3-link2':ps[2]['link2'],
               'productosimilar3-link3':ps[2]['link3'],
               'productosimilar1-price1':ps[0]['precio1'],
               'productosimilar1-price2':ps[0]['precio2'],
               'productosimilar1-price3':ps[0]['precio3'],
               'productosimilar2-price1':ps[1]['precio1'],
               'productosimilar2-price2':ps[1]['precio2'],
               'productosimilar2-price3':ps[1]['precio3'],
               'productosimilar3-price1':ps[2]['precio1'],
               'productosimilar3-price2':ps[2]['precio2'],
               'productosimilar3-price3':ps[2]['precio3'],
               'productosimilar1-shop1':ps[0]['tienda1'],
               'productosimilar1-shop2':ps[0]['tienda2'],
               'productosimilar1-shop3':ps[0]['tienda3'],
               'productosimilar2-shop1':ps[1]['tienda1'],
               'productosimilar2-shop2':ps[1]['tienda2'],
               'productosimilar2-shop3':ps[1]['tienda3'],
               'productosimilar3-shop1':ps[2]['tienda1'],
               'productosimilar3-shop2':ps[2]['tienda2'],
               'productosimilar3-shop3':ps[2]['tienda3']
            }
        )
def almacenarDatos(productos):
    arrayProdFinal=[]
    for i in (0,len(productos)-1):
        arrayProdFinal.append(productos[str(i)])
    return arrayProdFinal
    
def iniciarCodigo(file=None):
  resetearArreglosP()
  productos = leerJSON(file)
  productos=almacenarDatos(productos)
  for producto in productos:
    resetearArreglos()
    obtenerLinksPP(generarLink(producto))
    generarPS(producto)
    agregarInfoDiccionario(producto, preciosPPArray, tiendasPPArray, linksPPArray, arregloDicPS)
  driver.quit()
  jsonFinal = json.dumps(listFInal)
  return json.loads(jsonFinal)
