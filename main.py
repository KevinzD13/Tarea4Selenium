from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import os
import time

os.makedirs("capturas", exist_ok=True)

servicio = Service(ChromeDriverManager().install())
navegador = webdriver.Chrome(service=servicio)
navegador.maximize_window()

imagenes = []
resultado_final = "SUCCESS"

def esperar(segundos):
    time.sleep(segundos)

def guardar_captura(nombre):
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta = f"capturas/{nombre}_{fecha}.png"
    navegador.save_screenshot(ruta)
    print(f"Captura tomada: {ruta}")
    imagenes.append((nombre, ruta))

def crear_reporte():
    color = "#d4edda" if resultado_final == "SUCCESS" else "#f8d7da"
    texto_color = "#155724" if resultado_final == "SUCCESS" else "#721c24"

    html = f"""
    <html>
    <head>
        <title>Reporte ITLA</title>
        <style>
            .resultado {{
                background-color: {color};
                color: {texto_color};
                padding: 15px;
                border-radius: 10px;
                font-weight: bold;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <h1>Prueba Selenium - ITLA</h1>
        <p>Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <div class='resultado'>Resultado Final: {resultado_final}</div>
    """
    for titulo, ruta in imagenes:
        html += f"<h2>{titulo}</h2><img src='{ruta}' width='700'><br><br>"

    html += "</body></html>"
    with open("reporte.html", "w", encoding="utf-8") as archivo:
        archivo.write(html)
    print("Reporte generado: reporte.html")


try:
    print("Abriendo portal del ITLA")
    navegador.get("https://plataformavirtual.itla.edu.do/login/index.php")
    esperar(3)
    assert "itla" in navegador.current_url.lower()
    guardar_captura("01_Inicio")

    print("Probando credenciales incorrectas")
    user = navegador.find_element(By.ID, "username")
    pwd = navegador.find_element(By.ID, "password")
    user.send_keys("usuario_incorrecto")
    pwd.send_keys("clave_incorrecta")
    pwd.send_keys(Keys.RETURN)
    esperar(3)

    error = navegador.find_element(By.CLASS_NAME, "alert-danger")
    assert error.is_displayed()
    guardar_captura("02_Login_Fallido")

    print("Ingresando credenciales validas")
    WebDriverWait(navegador, 10).until(EC.presence_of_element_located((By.ID, "loginbtn")))
    navegador.find_element(By.ID, "username").clear()
    navegador.find_element(By.ID, "password").clear()
    navegador.find_element(By.ID, "username").send_keys("20231552")
    navegador.find_element(By.ID, "password").send_keys("KevinxD913$")

    try:
        recordar = navegador.find_element(By.ID, "rememberusername")
        if not recordar.is_selected():
            recordar.click()
            print("Casilla 'Recordar nombre de usuario' marcada.")
            guardar_captura("03_Recordar_Usuario")
    except:
        print("No se encontró la casilla 'Recordar nombre de usuario'.")

    navegador.find_element(By.ID, "password").send_keys(Keys.RETURN)

    WebDriverWait(navegador, 10).until(lambda d: "my" in d.current_url.lower())
    guardar_captura("04_Login_Exitoso")

    print("Entrando a mis cursos")
    cursos = WebDriverWait(navegador, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Mis cursos")))
    cursos.click()
    esperar(3)

    clase = navegador.find_element(By.LINK_TEXT, "Programación III (Virtual / Presencial) | 2025-C-1 | Kelyn Tejada Belliard")
    clase.click()
    esperar(3)
    guardar_captura("05_Curso_Abierto")

    print("Cerrando sesion")
    navegador.find_element(By.LINK_TEXT, "Cerrar sesión").click()
    esperar(3)
    assert "login" in navegador.current_url.lower()
    guardar_captura("06_Sesion_Cerrada")

except Exception as error:
    print("Ocurrió un error: ", error)
    resultado_final = "FAIL"
    guardar_captura("ERROR")
    crear_reporte()

finally:
    navegador.quit()
    if resultado_final == "SUCCESS":
        crear_reporte()
    print("Prueba finalizada")
