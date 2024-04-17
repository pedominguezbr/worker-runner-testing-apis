import math

import config
import logging
import time
import re
import pandas as pd
from multiprocessing.pool import ThreadPool
from datetime import timedelta
from datetime import timezone
from datetime import datetime
import json
import numpy as np

import requests

# # from requests import Request, Session
# from requests_toolbelt import MultipartEncoder

logging.basicConfig(level=config.agent["log_level"])
logger = logging.getLogger()
print("Iniciando...")

# initially open a session object
http = requests.Session()


def post_oauth_token(http, iteration):
    url = config.post_oauth_token["Url"]

    payload = {
        "grant_type": config.post_oauth_token["grant_type"],
        "client_id": config.post_oauth_token["client_id"],
        "client_secret": config.post_oauth_token["client_secret"],
        "scope": config.post_oauth_token["scope"],
    }

    headers = {
        "Connection": "keep-alive",
        "User-Agent": config.post_oauth_token["User_Agent"],
        "Accept": "*/*,",
        "Accept-Encoding": "gzip, deflate, br",
        "Host": config.post_oauth_token["Host"],
    }

    # execute requests continuously
    while True:
        try:
            # response = http.post(url, data=multipart_data, headers=headers)
            if config.agent["use_keep_alive"] == True:
                response = http.post(url, headers=headers, data=payload, verify=False)
            else:
                response = requests.request(
                    "POST", url, headers=headers, data=payload, verify=False
                )

            break
            # process response
        except requests.exceptions.RequestException:
            http = requests.Session()
            continue
        except requests.exceptions.ConnectionError:
            break
        # process respons
    # wait for seconds
    # print(
    #     "container ready, waiting another tiempo_espera_sec seconds to ensure everything is set up"
    # )
    time.sleep(config.agent["tiempo_espera_sec"])
    logger.debug("response: {}".format(response.text))
    logger.info(
        "Iteration {} result a api: {}, status code:{}".format(
            iteration, url, response.status_code
        )
    )
    return response


def run_process(dflote, index, http):
    lista_tabla_procesar = []
    logger.debug("== Ingreso a la funcion [run_process] {} ===".format(index))
    logger.info("dflote:{}".format(dflote))

    for index, row in dflote.iterrows():
        logger.debug("Enviando a api: {}".format(row))

        response = post_oauth_token(http, row["info_Data"])

        logger.debug("response: {}".format(response.text))
        logger.info(
            "Iteration {} result a api: {}, status code:{}".format(
                row["info_Data"],
                config.post_oauth_token["Url"],
                response.status_code,
            )
        )
        dflote.loc[index, "status_code"] = response.status_code
        if response.status_code > 200:
            dflote.loc[index, "desc_code"] = response.text
    # ends the request sending process
    lista_tabla_procesar.append(dflote)
    return {
        "lista_tabla_procesar": (
            pd.DataFrame()
            if len(lista_tabla_procesar) == 0
            else pd.concat(lista_tabla_procesar)
        )
    }


def init_process():
    now1 = datetime.now()
    fecha = now1.strftime("%Y%m%d%H%M")
    fechaproceso = str(fecha)
    # print(fechaproceso)

    name_file = f"{config.agent['name_file_csv']}-{fechaproceso}.csv"

    total_registros = 0

    dataObtenida = np.arange(config.agent["total_request"])

    logger.info("dataObtenida:{}".format(dataObtenida))
    # Obteniendo el total de registros a procesar
    total_registros = len(dataObtenida)

    logger.info("TOTAL_REGISTROS:{}".format(len(dataObtenida)))

    dflote = pd.DataFrame(
        {
            "info_Data": dataObtenida,
            "error": False,
            "status_code": 0,
            "desc_code": "",
        }
    )

    lista = np.array_split(dflote, config.agent["nivel_paralelismo"])

    if len(lista) < 1:
        return False

    print("total Registros Validacion: " + str(total_registros))
    if total_registros > 0:
        pool = ThreadPool(len(lista))
        hilos = []
        for i in range(0, len(lista)):
            hilos.append(
                pool.apply_async(
                    run_process,
                    args=(
                        lista[i],
                        i,
                        http,
                    ),
                )
            )
        # print(f"hilos {hilos}")
        pool.close()
        pool.join()
        pre_results = [r.get() for r in hilos]

        # Get dataframe processed
        df_lista_tabla_procesar = pd.DataFrame()
        for item in pre_results:
            if not item["lista_tabla_procesar"].empty:
                df_correctos = pd.DataFrame(item["lista_tabla_procesar"])
                df_lista_tabla_procesar = pd.concat(
                    [df_lista_tabla_procesar, df_correctos]
                )

        df_lista_tabla_procesar.to_csv(name_file, mode="a", index=False, header=True)

        print(f"df_lista_tabla_procesar: {df_lista_tabla_procesar}")
        ###################################
        name_file
        logger.info("Archivo CSV generado: {}".format(name_file))
        print("FINALIZA PROCESO DE DATA")
    else:
        print("NO EXISTE DATA TERMINA PROCESO")


result = init_process()
