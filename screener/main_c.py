import pandas as pd
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import psycopg2
from sqlalchemy import create_engine
import time

chromedriver_path = "chromedriver.exe"

def screener_login(username, password):
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service)
    driver.get("https://www.screener.in/login/?")
    time.sleep(1)

    email_login = driver.find_element(By.NAME, "username")
    password_input = driver.find_element(By.NAME, "password")

    email_login.send_keys(username)
    password_input.send_keys(password)

    login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
    login_button.click()
    time.sleep(2)
    return driver

def scrape_watchlist(driver, watchlist_href: int):
    dropdown_button = driver.find_element(By.XPATH, "//i[@class='icon-down ink-700 smaller']")
    dropdown_button.click()
    time.sleep(1)

    watchlist_t = driver.find_element(By.XPATH, '/html/body/div/div[2]/main/div[1]/div[1]/div/ul/li[2]/a')
    watchlist_t.click()

    watchlist_view = driver.find_element(By.XPATH, f'//a[@href="/watchlist/{watchlist_href}/"]')
    watchlist_view.click()

    header = driver.find_elements(By.TAG_NAME, 'th')
    col = []
    for i in header:
        if i.text not in col:
            col.append(i.text)

    rows = driver.find_elements(By.TAG_NAME, 'tr')
    data = []
    for i in rows:
        cells = i.find_elements(By.TAG_NAME, 'td')
        a = [cell.text for cell in cells]
        if a:
            a.pop(1)
            data.append(a)

    df = pd.DataFrame(data, columns=col)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('.', '_')
    df['load_dttm'] = datetime.now()
    return df

def postgres_load(df, table_name):
    engine = create_engine('postgresql+psycopg2://myuser:mypassword@localhost:5432/raw_stock_data')
    conn = psycopg2.connect(
        host="localhost",
        database="raw_stock_data",
        user="myuser",
        password="mypassword",
        port=5432
    )
    df.to_sql(name=table_name, con=engine, if_exists='append', index=False)
    cursor = conn.cursor()

    alter_table = f"""ALTER TABLE {table_name}
    ADD COLUMN IF NOT EXISTS id BIGSERIAL;"""
    cursor.execute(alter_table)
    # except psycopg2.errors.DuplicateColumn:
    #     print(f"'id' column already exists in {table_name}, skipping it.")

    print("data inserted successfully!")

def main():
    try:
        func_driver = screener_login("mexof92729@hadvar.com", "garima@57")
        df_func = scrape_watchlist(func_driver, 9035338)
        print("functional watchlist: \n", df_func.head())
        postgres_load(df_func, "conco_r_func_table")
        func_driver.quit()

    except Exception as e:
        print("Error in functional data process: ", e)


if __name__ == "__main__":
    main()
