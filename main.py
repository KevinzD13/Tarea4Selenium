import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import os
import time

os.makedirs("capturas", exist_ok=True)
imagenes = []

@pytest.fixture
def navegador():
    servicio = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=servicio)
    driver.maximize_window()
    yield driver
    driver.quit()

def esperar(segundos):
    time.sleep(segundos)

def guardar_captura(driver, nombre):
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    ruta = f"capturas/{nombre}_{fecha}.png"
    driver.save_screenshot(ruta)
    print(f"Captura tomada: {ruta}")
    imagenes.append((nombre, ruta))

def crear_reporte(resultado_final):
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

def test_portal_itla(navegador):
    resultado_final = "SUCCESS"
    try:
        navegador.get("https://plataformavirtual.itla.edu.do/login/index.php")
        esperar(2)
        assert "itla" in navegador.current_url.lower()
        guardar_captura(navegador, "01_Inicio")

        navegador.find_element(By.ID, "username").send_keys("usuario_incorrecto")
        navegador.find_element(By.ID, "password").send_keys("clave_incorrecta", Keys.RETURN)
        esperar(2)
        error = navegador.find_element(By.CLASS_NAME, "alert-danger")
        assert error.is_displayed()
        guardar_captura(navegador, "02_Login_Fallido")

        navegador.find_element(By.ID, "username").clear()
        navegador.find_element(By.ID, "password").clear()
        navegador.find_element(By.ID, "username").send_keys("20231552")
        navegador.find_element(By.ID, "password").send_keys("KevinxD913$")

        try:
            recordar = navegador.find_element(By.ID, "rememberusername")
            if not recordar.is_selected():
                recordar.click()
                print("Casilla marcada")
                guardar_captura(navegador, "03_Recordar_Usuario")
        except:
            print("Casilla no encontrada")

        navegador.find_element(By.ID, "password").send_keys(Keys.RETURN)
        WebDriverWait(navegador, 10).until(lambda d: "my" in d.current_url.lower())
        guardar_captura(navegador, "04_Login_Exitoso")

        cursos = WebDriverWait(navegador, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Mis cursos")))
        cursos.click()
        esperar(2)

        clase = navegador.find_element(By.LINK_TEXT, "Programación III (Virtual / Presencial) | 2025-C-1 | Kelyn Tejada Belliard")
        clase.click()
        esperar(2)
        guardar_captura(navegador, "05_Curso_Abierto")

        navegador.find_element(By.LINK_TEXT, "Cerrar sesión").click()
        esperar(2)
        assert "login" in navegador.current_url.lower()
        guardar_captura(navegador, "06_Sesion_Cerrada")

    except Exception as e:
        print("Error:", e)
        guardar_captura(navegador, "ERROR")
        resultado_final = "FAIL"
        raise AssertionError("Prueba fallida: " + str(e))
    finally:
        crear_reporte(resultado_final)

if __name__ == "__main__":
    pytest.main([__file__, "--html=resultado_pytest.html"])