from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from solver import Solver


def _get_driver() -> Chrome:
    service = Service(
        executable_path='C:\Program Files\Google\Chrome\chromedriver.exe'
    )

    options = Options()

    options.add_argument('start-maximized')

    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    return Chrome(
        service=service,
        options=options
    )


if __name__ == '__main__':
    driver = _get_driver()
    
    try:
        solver = Solver(driver)
        
        print(
            f'Palavra encontrada!\nA palavra era "{solver.word}".' if solver.solve() else 'Palavra não encontrada!'
        )

        guesses = solver.guesses

        print(f'Quantidade de tentativas: {len(guesses)}.')
        print(f'Tentativas: {", ".join(guesses)}.')

    finally:
        driver.quit()
