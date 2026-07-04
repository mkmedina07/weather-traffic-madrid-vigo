import os
import sys
import unittest
from unittest.mock import MagicMock
import importlib


class TestWeather(unittest.TestCase):
    def test_obtener_clima_devuelve_datos(self):
        # Pre-insert a mocked 'requests' module to avoid importing the real package
        mock_requests = MagicMock()
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "weather": [{"description": "cielo despejado"}],
            "main": {"temp": 20.5, "feels_like": 19.0, "humidity": 55, "pressure": 1012},
            "wind": {"speed": 3.2}
        }
        mock_requests.get.return_value = mock_response

        sys.modules['requests'] = mock_requests

        # Ensure the module is imported fresh so it uses the mocked requests
        if 'utils.weather' in sys.modules:
            del sys.modules['utils.weather']
        weather = importlib.import_module('utils.weather')

        # Set the environment variable for the API key
        os.environ['OPENWEATHER_API_KEY'] = 'test_api_key'

        resultado = weather.obtener_clima("Madrid")

        self.assertEqual(resultado["ciudad"], "Madrid")
        self.assertEqual(resultado["descripcion"], "cielo despejado")
        self.assertEqual(resultado["temperatura"], 20.5)
        self.assertEqual(resultado["humedad"], 55)
        self.assertEqual(resultado["viento"], 3.2)
        self.assertNotIn("error", resultado)


if __name__ == "__main__":
    unittest.main()
