## Author: Jessica Chew
## Version: 0.0.0.0
## Date: 10 April 2023
##############################################
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
##############################################

st.set_page_config(layout="wide")

## UBI section ## experimental
st.header("Easily estimate how you could benefit from a Universal Basic Income")
st.subheader("BASIC INCOME AUSTRALIA - EXPERIMENTAL POLICY MODELLING TOOL")
st.write("BIA proposes a AUD 500/week (26,000/year) universal basic income paid to every adult 18+ years in Australia without conditions or targeting (details TBC)")
st.write("The BIA policy recovers the UBI payment at 32.26 percent of an individual's gross salary up to 80,600. The 32.26 percent clawback rate was chosen as it represents the dollar amount of annual UBI paid to an individual out of the 80,600 per year threshold. (32.26% = 26,000/80,600)")
st.write("This means an 80,600 per annum salary is the threshold at which an individual ceases to be a net beneficiary.")
st.write("If you earn more than 80,600 a year, it means you will still receive the regular UBI payment like everyone else however the full UBI payment ($26K) will be recovered through the group tax system.")
st.write("If you earn less than 80,600 a year, you become a net UBI beneficiary on a sliding scale. This means, the more you earn, the lower the proportion of the $500/week UBI you will receive. The less you earn, the more of the UBI payment you get to keep.")
st.write("See what UBI means for you by entering your annual salary.")


# Income input
pi = st.number_input ("What is your annual personal income?" , value = 20000) ## Default to $20K for now. Future idea: show nothing until the user inputs a salary

# Calculate barebones personal income tax for FY 2022-2023
# https://www.ato.gov.au/Rates/Individual-income-tax-rates/
def tax_payable(pi):
    if ((pi > 0) and (pi <= 18200)):
            tax = 0
    elif ((pi >= 18201) and (pi <= 45000)):
            tax = (pi - 18200) * 0.19
    elif ((pi >= 45001) and (pi <= 120000)):
            tax = ((pi - 45000) * 0.325) + 5092
    elif ((pi >= 120001) and (pi <= 180000)):
            tax = ((pi - 120000) * 0.37) + 29467
    elif pi >= 180001:
            tax = ((pi - 180000) * 0.45) + 51667
    return(tax)

#tax_payable(60000)


## Set up the outputs at different time levels

## Basic income payment
weekly_ubi_level = 500
annual_ubi = weekly_ubi_level*52
weekly_ubi = weekly_ubi_level
fornightly_ubi = weekly_ubi_level*2

##Basic income clawback level
clawback_amount = 26000

## Tax payable
annual_tax_payable = round(tax_payable(pi),0)
weekly_tax_payable = round((tax_payable(pi))/52,0)
fortnightly_tax_payable = round((tax_payable(pi))/26,0)

## Gross earned income
annual_gross_income = round(pi,0)
weekly_gross_income = round((pi/52),0)
fortnightly_gross_income = round((pi/26),0)

## Net earned income
annual_net_income = round(pi-(tax_payable(pi)),0)
weekly_net_income = round((pi-(tax_payable(pi)))/52,0)
fortnightly_net_income = round((pi-(tax_payable(pi)))/26,0)

## UBI recovery "clawback" function
def clawback(annual_gross_income):
    if (annual_gross_income > 80600):
        clawback = clawback_amount
    elif (annual_gross_income <= 80600):
        clawback = round(annual_gross_income * 0.3226 ,0)
    return(clawback)

net_ubi_benefit = clawback_amount - clawback(annual_gross_income) 

def ubi_recovery_explainer(annual_gross_income):
    if (annual_gross_income > 80600):
        explainer = "(Because your salary exceeds the annual threshold the whole basic income is recaptured)"
    elif (annual_gross_income <= 80600):
        explainer = "($" + str(round(annual_gross_income,0)) + " x 32.26%)"
    return(explainer)

net_benefit = annual_net_income + net_ubi_benefit

def net_benefit_explainer(annual_gross_income):
    if (annual_gross_income > 80600):
        explainer = "Because your salary exceeds the annual threshold you do not receive a net UBI benefit but neither are you worse off (your annual net take home pay in both scenarios is the same) " ## not to mention potential interest rate gains from being paid a UBI in advance?!?!?
    elif (annual_gross_income <= 80600):
        explainer = "You are " + str(net_benefit - annual_net_income) + " dollars ahead compared to not receiving a 500 dollar/week UBI" + " (" + str(round(net_benefit,0)) + "-" + str(round(annual_net_income,0)) +")"
    return(explainer)





## Set up the two columns
col1, col2 = st.columns(2)

with col1:
    st.subheader('Current personal income taxation regime (no UBI)')
    st.write("Annual gross income:" , pi )
    st.write("Annual tax payable:" , annual_tax_payable , "or" , round((annual_tax_payable/pi)*100,0) , "percent of your income")
    st.write("Annual net take home pay:" , annual_net_income)
    st.markdown(""" <span style="font-family: sans-serif; font-size: 8pt;">Tax calculations are based on the ATO 2022-2023 personal income tax schedule: https://www.ato.gov.au/rates/individual-income-tax-rates/</span>""", unsafe_allow_html=True)
    st.markdown(""" <span style="font-family: sans-serif; font-size: 8pt;">Note: This calculator does not cover any HECS-HELP repayments, Medicare levy, Medicare levy surcharge, working holiday makers' tax obligations nor the First Home Super Saver (FHSS) scheme. It simply models the latest Australian personal income tax structure assuming you were a full-year resident for tax purposes.</span>""", unsafe_allow_html=True)
    
with col2:
    st.subheader("BIA's Proposed UBI mechanism")
    st.write("Annual gross income:" , pi )
    st.write("Annual tax payable:" , annual_tax_payable , "or" , round((annual_tax_payable/pi)*100,0) , "percent of your income")
    st.write("UBI recovery amount:" , clawback(annual_gross_income) , ubi_recovery_explainer(annual_gross_income)) 
    st.write("Net UBI" , net_ubi_benefit , "(" , "$26000 -" , clawback(annual_gross_income) ,")")
    st.write("Annual net take home pay + net UBI" , net_benefit, "(" , annual_net_income , "+" , net_ubi_benefit, ")")
    netbenexp = net_benefit_explainer(annual_gross_income)
    style = "<span style='font-family: sans-serif; font-size: 18pt;'>{}</span>".format(netbenexp)
    st.markdown(style, unsafe_allow_html=True)

    

## next steps (from 9 April 2023 onwards)
## Finesse the blurb
## Finesse the code labels to accord with the accounting language
## Make sure there are no errors when the page first loads (and there's no income input yet)
## Figure out versioning structure - official
## Add link to Git
## Publish
## Share with Michael alongside list of next steps and ideas
## e.g., model line graph, do different scenarios with HECs, people receiving DSP etc and also different time drop downs, add language about two-part tax, add colour
## feedback form


