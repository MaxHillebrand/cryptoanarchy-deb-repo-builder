#!/usr/bin/python3

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import subprocess
from time import sleep
import sys

def eprint(msg):
    print(msg, file=sys.stderr)

ret = 0

default_domain = subprocess.run(["sudo", "/usr/share/selfhost/lib/get_default_domain.sh"], stdout=subprocess.PIPE).stdout.decode("utf-8")

eprint("The default domain is " + default_domain)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("ignore-certificate-errors")
driver = webdriver.Chrome(chrome_options=chrome_options)

eprint("Registering an admmin account")

driver.get(default_domain + "/btcpay-rt")
driver.find_element_by_id("Email").send_keys("admin@example.com")
driver.find_element_by_id("Password").send_keys("super secure password")
driver.find_element_by_id("ConfirmPassword").send_keys("super secure password")
driver.find_element_by_id("ConfirmPassword").send_keys(Keys.RETURN)

eprint("Setting up a test store")

driver.get(default_domain + "/btcpay-rt/stores/create")
driver.find_element_by_id("Name").send_keys("Test")
driver.find_element_by_id("Name").send_keys(Keys.RETURN)
store_id = driver.find_element_by_id("Id").get_attribute("value")

eprint("Setting up a chain hot wallet")

driver.get(default_domain + "/btcpay-rt/stores/" + store_id + "/derivations/BTC")
driver.find_element_by_id("import-from-btn").click()
driver.find_element_by_id("nbxplorergeneratewalletbtn").click()
sleep(3)
driver.find_element_by_id("SavePrivateKeys").click()
driver.find_element_by_id("btn-generate").click()

eprint("Waiting for genmacaroon")

while subprocess.call(["sudo", "test", "-e", "/var/lib/lnd-system-regtest/invoice/invoice+readonly.macaroon"]) != 0:
    sleep(1)

eprint("Setting up lightning")

driver.get(default_domain + "/btcpay-rt/stores/" + store_id + "/lightning/BTC")
driver.find_element_by_id("internal-ln-node-setter").click()
driver.find_element_by_id("save").click()

eprint("Setting up PayJoin")

driver.find_element_by_id("PayJoinEnabled").click()
driver.find_element_by_id("Save").click()

eprint("Creating an invoice")

driver.get(default_domain + "/btcpay-rt/invoices/create/")
driver.find_element_by_id("Amount").send_keys("10")
driver.find_element_by_id("Amount").send_keys(Keys.RETURN)

eprint("Retrieving payment details")

driver.find_element_by_class_name("invoice-checkout-link").click()
payment_link = driver.find_element_by_class_name("payment__details__instruction__open-wallet__btn").get_attribute("href")
payment_link = payment_link[len("bitcoin:"):]
address = payment_link.split('?')[0]
amount_pos = payment_link.find("amount=")
amount_pos += len("amount=")
amount_end = payment_link.find("&", amount_pos)

if payment_link.find("pj=") < 0:
    eprint("PayJoin disabled")
    ret = 1

if amount_end < 0:
    amount_end = len(payment_link)

amount = payment_link[amount_pos:amount_end]
amount_sats = int(float(amount) * 100000000)

eprint("Attempting to pay " + str(amount_sats) + " sats to " + address)
subprocess.run(["sudo", "lncli", "--network", "regtest", "sendcoins", address, str(amount_sats)])

sleep(10)

if driver.find_element_by_class_name("success-message").text != "This invoice has been paid":
    eprint("Failed to pay chain address")
    ret = 1

eprint("Creating an invoice")

driver.get(default_domain + "/btcpay-rt/invoices/create/")
driver.find_element_by_id("Amount").send_keys("10")
driver.find_element_by_id("Amount").send_keys(Keys.RETURN)

eprint("Retrieving Lightning invoice")

driver.find_element_by_class_name("invoice-checkout-link").click()
driver.find_element_by_class_name("payment__currencies").click()

for element in driver.find_elements_by_class_name("vexmenuitem"):
    a = element.find_element_by_css_selector("a")
    if a.text.find("Lightning") > 0:
        a.click()
        break

payment_link = driver.find_element_by_class_name("payment__details__instruction__open-wallet__btn").get_attribute("href")

invoice = payment_link[len("lightning:"):]

subprocess.run(["sudo", "-u", "lnd-test-1", "/usr/lib/lncli/lncli", "--network", "regtest", "--rpcserver", "127.0.0.1:9802", "payinvoice", "-f", invoice])

sleep(5)

if driver.find_element_by_class_name("success-message").text != "This invoice has been paid":
    eprint("Failed to pay Lightning invoice")
    ret = 1

sys.exit(ret)
