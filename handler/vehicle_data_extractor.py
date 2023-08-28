import boto3
import io

from loguru import logger
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from playwright_stealth import stealth_async
from uuid import uuid4


class VehicleDataExtractor:

    # Playwright configuration
    HEADLESS = True
    CHROMIUM_ARGS = [
        "--no-sandbox",
        "--disable-blink-features=AutomationControlled",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-setuid-sandbox",  # Disable the setuid sandbox (Linux only)
        "--enable-logging",
        "--hide-scrollbars",
        "--ignore-default-args=--enable-automation",
        "--ignore-certificate-errors",
        "--log-level=0",
        "--no-zygote",
        "--single-process",
        "--v=0",
        "--window-size='1920x1080'",
        # f"--data-path={TMP_FOLDER}/data-path",
        # f"--homedir={TMP_FOLDER}",
        # f"--disk-cache-dir={TMP_FOLDER}/cache-dir",
        # f"--user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"",
    ]
    SLOW_MO = 5000
    TIMEOUT = 20000
    MAX_RETRIES = 3
    MONITOR_NETWORK = False

    def __init__(self):
        # TODO: Model SpiderState with pydantic
        self.state = {
            # Core
            "status": "INIT",
            "message": "init execution",
            "success": False,
            "traceback": None,
            # S3
            "keypath": None,
            "bucket": None,
            # Spider
            "patente": None,
            "filename": None,
            "vehiculo": {}
        }
        logger.info(f"State INIT: {self.state}")

        # S3
        session = boto3.Session()
        self.s3client = session.client("s3")

    async def run(self, __input: dict) -> dict:
        self.state["status"] = "RUNNING"
        self.state["message"] = "running spider"
        self.state = self.state | __input
        logger.info(f"State RUNNING: {self.state}")

        # Execution workflow
        try:
            # Playwright automation
            async with async_playwright() as playwright:
                return await self._init_automation(playwright)

        except Exception as error:
            logger.error(f"Run exception: {error}")
            self.state["status"] = "ERROR"
            self.state["message"] = "failed execution"
            self.state["success"] = False
            self.state["traceback"] = repr(error)

            logger.debug(f"State FAILURE: {self.state}")
            raise BaseException(self.state)

    async def _init_automation(self, playwright) -> dict:
        if self.HEADLESS:
            self.CHROMIUM_ARGS.append("--headless=new")
        browser = await playwright.chromium.launch(headless=self.HEADLESS, slow_mo=self.SLOW_MO, args=self.CHROMIUM_ARGS)

        # Create new incognito browser context.
        context = await browser.new_context()
        context.set_default_timeout(self.TIMEOUT)

        # Create new page in a pristine context.
        page = await context.new_page()
        
        # Stealth
        await stealth_async(page)

        if self.MONITOR_NETWORK:
            # Monitor network traffic
            # Log network traffic for easier debugging
            await context.route("**/*", self._handle_route)
            await context.route("**/*.{png,jpg,jpeg}", lambda route: route.abort())
            # await context.route_from_har()

        # Debugger breakpoint
        # await page.pause()

        # Landing page with retry
        for i in range(self.MAX_RETRIES):
            try:
                await page.goto(
                    f"https://soapweb.bciseguros.cl/web/DatosVehiculo?Convenios=700660&p={self.state['patente']}",
                    referer="https://google.com/",
                    wait_until="domcontentloaded"
                )
                break

            except PlaywrightTimeoutError as error:
                if i <= 1:
                    await page.reload(wait_until="domcontentloaded")
                    continue

                logger.error(f"Loading page error: {error}")
                screenshot: bytes = await page.screenshot(full_page=True)
                _image_to_s3(
                    image=screenshot,
                    filename=f"loading_error_{uuid4()}.png",
                    keypath=self.state["keypath"],
                    bucket=self.state["bucket"],
                    s3client=self.s3client
                )
                raise Exception(f"Loading page error: {error}")
        logger.debug(f"Page loaded successfully")

        # TODO: wait for load page

        # Extract autocompleted data
        await page.wait_for_timeout(5000)

        # Datos vehiculo
        patente = await page.locator("#TbPatente").get_attribute("value")
        logger.debug(f"Patente: {patente}")

        # Little logic validation
        if self.state["patente"].upper() != patente.upper():
            logger.error("La patente buscada y la patente en mostrada en la web no coinciden.")
            raise Exception("PatenteValidationException")

        año_vehiculo = await page.locator("#TbAno").get_attribute("value")
        logger.debug(f"Año vehiculo: {año_vehiculo}")

        tipo_vehiculo = await page.locator("#DdlTipoVehiculo option[selected='selected']").inner_text()
        logger.debug(f"Tipo vehiculo: {tipo_vehiculo}")

        marca_vehiculo = await page.locator("#DdlMarca option[selected='selected']").inner_text()
        logger.debug(f"Marca vehiculo: {marca_vehiculo}")

        modelo_vehiculo = await page.locator("#DdlModelo option[selected='selected']").inner_text()
        logger.debug(f"Modelo vehiculo: {modelo_vehiculo}")

        num_motor = await page.locator("#TbNroMotor").get_attribute("value")
        logger.debug(f"Numero motor: {num_motor}")

        # Datos propietario
        rut_propietario = await page.locator("#TbRut").get_attribute("value")
        logger.debug(f"Rut propietario: {rut_propietario}")

        nombres_propietario = await page.locator("#TbNombres").get_attribute("value")
        logger.debug(f"Nombres propietario: {nombres_propietario}")

        primer_apellido_propietario = await page.locator("#TbApellidoPaterno").get_attribute("value")
        logger.debug(f"Primer apellido propietario: {primer_apellido_propietario}")

        segundo_apellido_propietario = await page.locator("#TbApellidoMaterno").get_attribute("value")
        logger.debug(f"Segundo apellido propietario: {segundo_apellido_propietario}")

        # TODO: Fill missing data
        # self.state["telefono"] = "992736388"
        # await page.locator("#TbTelefono").type(self.state["telefono"])

        # self.state["email"] = "jegajardog@gmail.com"
        # await page.locator("#TbEmail").type(self.state["email"])

        # Confirm checkbox
        # await page.locator("#ContentPlaceHolder1_chkDatosVehiculoPropietario").check()
        
        # Debugger breakpoint
        # await page.pause()

        # Submit
        # await page.locator("#BtnContinuar").dispatch_event("click")

        # Screenshot
        screenshot: bytes = await page.screenshot(full_page=True)
        _image_to_s3(
            image=screenshot,
            filename="proof.png",
            keypath=self.state["keypath"],
            bucket=self.state["bucket"],
            s3client=self.s3client
        )

        # gracefully close up everything
        # await context.close()
        # await browser.close()

        # This state is added when last relevant data is extracted
        self.state["status"] = "OK"
        self.state["message"] = "Busqueda exitosa de informacion del vehiculo."
        self.state["success"] = True
        self.state["vehiculo"] = {
            "patente": patente,
            "año_vehiculo": año_vehiculo,
            "tipo_vehiculo": tipo_vehiculo,
            "marca_vehiculo": marca_vehiculo,
            "num_motor": num_motor
        }
        logger.info(f"State SUCCESS: {self.state}")
        return self.state

    async def _handle_route(self, route):
        """
        Network Route.
        Handles all traffic that goes through the browser.
        Must be used 
        """
        request = route.request
        logger.debug(f"Route url ({request.method}): {request.url}")

        # if request.method == "GET":
        #     self.__request_headers = request.headers
        #     logger.info(f"Request headers: {self.__request_headers}")
        #
        #     self.__request_url = request.url
        #     logger.info(f"Request URL: {self.__request_url}")

        await route.continue_()


def _image_to_s3(image: bytes, filename: str, keypath: str, bucket: str, s3client):
    """
    Save image into S3 bucket.
    :param image: bytes string representing an image data.
    :param filename: Name of file (s3 object) to be saved, include the extension of the file.
    :param keypath: S3 bucket path where to store the file.
    :param bucket: S3 bucket name.
    :param s3client: S3 client or session.
    :return: None
    """
    key = f"{keypath}/{filename}"
    status = s3client.put_object(Bucket=bucket, Key=key, Body=io.BytesIO(image))
    logger.debug(f"Save screenshot in {key}...{status['ResponseMetadata']['HTTPStatusCode']}")
