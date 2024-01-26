## Author: Jessica Chew
## Version: 0.0.1
## Date: 25 Jan 2024
## Updates include: modularising the income threshold, clawback amounts and clawback rates
## Updating the weekly UBI amount to $600 and the threshold to $96,714
## Updating the tax schedule labels to 2023-2024 (although the rates are the same as the previous financial year)
## Added more information about the latest Henderson Poverty Line data (June quarter 2023)
##############################################
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
##############################################

st.set_page_config(layout="centered")
st.image('BIA logo.png' , width=150)
st.header("Basic Income Australia's Benefit Calculator")
st.subheader("BIA proposes a universal basic income of AU$600/week - see what it means for you")

tab1 , tab2 , tab3 = st.tabs(["Calculator" , "Policy overview" , "Provide feedback"])

## CALCULATOR PAGE ##
with tab1:
# Income input - use Latex text to adjust input prompt font size
# Useful size guide here: https://stackoverflow.com/questions/77377439/how-to-change-font-size-in-streamlit

## Personal income input box
    # Hacky solve, when the app initialises and is empty, it throws a value error. In this case, set the personal income to 0
    try:
        # Potential Streamlit bug for 'st.number_input' - the 'placeholder' argument is not showing up despite being the latest version 1.29
        # To raise with Streamlit later https://docs.streamlit.io/library/api-reference/widgets/st.number_input
        # Meanwhile, hack by using 'st.text_input' and then wrap the output as an integer in the try statement
        input = st.text_input (label = r"$\textsf{\Large What is your annual personal income before tax?}$" , max_chars = 8, placeholder = "Enter income here")
        ## Input quality checks, make sure there are no negative numbers or strings
        if input.strip():
            try:
                # Attempt to convert the input to an integer. PI = personal income
                pi = int(input)

                # Check if income entered is <0
                if pi <0:
                    st.warning("Error: Please enter a non-negative number to the nearest dollar, e.g., 45000")
                    pi = 88888888  # Set pi to 0 if less than 0

            ## If pi can't be converted to an integer, throw the valid numbers error
            except ValueError:
                st.warning("Error: Please enter valid numbers only to the nearest dollar, e.g., 45000")
                pi = 88888888
        ## If nothing has been entered, use 0 as a placeholder to prevent errors
        ##else: pi = 0
        else: pi = 88888888
    ## If nothing has been entered, use 0 as a placeholder to prevent errors
    except ValueError:
        pi = 0

## FUNCTIONS AND FOMRATTING set up

# Custom CSS to set the font in the 'see calculation' expander
custom_css = """
<style>
code {
    font-size: 13px;  /* Adjust the font size as needed */
    color: #f63366;
}
</style>
"""

# Displays for the custom CSS
st.markdown(custom_css, unsafe_allow_html=True)
clawback_rate = 0.3226
threshold_annual = 96714

## Functions
# Calculate barebones personal income tax for FY 2023-2024
# https://www.ato.gov.au/tax-rates-and-codes/tax-rates-australian-residents
def tax_payable(pi):
    tax=0
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
weekly_ubi_level = 600
annual_ubi = weekly_ubi_level*52
weekly_ubi = weekly_ubi_level
fornightly_ubi = weekly_ubi_level*2

##Basic income clawback level
clawback_amount = 31200

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
    if (annual_gross_income >= threshold_annual):
        clawback = clawback_amount
    elif (annual_gross_income < threshold_annual):
        clawback = round(annual_gross_income * clawback_rate ,0)
    return(clawback)

net_ubi_benefit = clawback_amount - clawback(annual_gross_income) 

def ubi_recovery_explainer(annual_gross_income):
    if (annual_gross_income >= threshold_annual):
        explainer = "Because your salary exceeds the annual threshold the whole basic income is recaptured"
    elif (annual_gross_income < threshold_annual):
        explainer = ""+ str(round(annual_gross_income,0)) + " x 32.26%"   
    return(explainer)
    
net_benefit = annual_net_income + net_ubi_benefit

## Default always-on result explainer
def net_benefit_explainer_brief(annual_gross_income):
    if (annual_gross_income >= threshold_annual):
        explainer = (
        "<b style='font-size: 17px;'>Because your salary exceeds the annual threshold of &#36;97,714 <span style='color:#2874A6;'>you do not receive a net UBI benefit but neither are you worse off </span> (as your after-tax take home pay remains the same) </b> " 
        )
    elif (annual_gross_income < threshold_annual):
        explainer = (
            "<b style='font-size: 25px;'>Your income would be enhanced by "
            "<span style='color: #16A085;'>&#36;"
            + str('{:,}'.format(int(round(net_benefit - annual_net_income, 0))))
            + "</span> per year after taxes under the BIA policy</b>"
        )
    return(explainer)


def net_benefit_explainer_detailed(annual_gross_income):
    if (annual_gross_income >= threshold_annual):
        explainer = (
        "<b style='font-size: 17px;'>Because your salary exceeds the annual threshold of &#36;97,714 <span style='color:#2874A6;'>you do not receive a net UBI benefit but neither are you worse off </span> (as your after-tax take home pay remains the same in both scenarios) </b> " 
        )
    elif (annual_gross_income < threshold_annual):
        explainer = (
            "<b style='font-size: 17px;'>You are "
            "<span style='color: #16A085;'>&#36;" 
            + str('{:,}'.format(int(net_benefit - annual_net_income)) )
            + " </span> ahead per year compared to not receiving a UBI" 
            ## formatting the calculation to the coding font
            + " (" f"  <code>{str(int(net_benefit))}</code>" + " - " + f"  <code>{str(int(annual_net_income))}</code>" + ")"
        )
    return(explainer)

## POLICY OVERVIEW PAGE ##
with tab2:
## Policy overview page

    ### PREPARE DATA MODEL FOR CHARTING ### 
    ## Create the tax and UBI payable data model for chart
    income_data = list(range(0, 110000, 5000))
    df = pd.DataFrame({'Gross earned income':income_data})
    # Include the value 80,600 for treshold data visualisation
    ##df = pd.concat([df, pd.DataFrame({'Gross earned income': [threshold_annual]})])  ## to delete
    # Sort the DataFrame by 'Gross earned income'
    df = df.sort_values(by='Gross earned income').reset_index(drop=True)

    # Apply tax function to calculate 'tax' for each 'Gross earned income'
    df['Tax'] = df['Gross earned income'].apply(tax_payable)
    # Calculate net earned income after personal income tax
    df['Net earned income'] = df['Gross earned income'] - df['Tax']

    # Create 'UBI Benefit' column based on conditions
    df['UBI Benefit'] = clawback_amount-df['Gross earned income'].apply(lambda x: x * clawback_rate if x < threshold_annual else clawback_amount)
    df['Net final income'] = df['Net earned income'] + df['UBI Benefit']
    

    # Extra UBI benefit calculation for the UBI Benefit chart hover functionality later
    ubi_benefit_hover_list = [clawback_amount - x * clawback_rate if x < threshold_annual else clawback_amount for x in df['Gross earned income']]

    ### START BUILDING THE PLOTLY CHARTS ###
    fig = go.Figure()

    ## Net earned income view
    fig.add_trace(go.Bar(
        x = df['Gross earned income'],
        y = df['Net earned income'],
        name = 'Net earned income <br>(Gross income less 2023/24 <br> personal income tax, no UBI)',
        marker_color = 'blue',
        hovertemplate = ## Formatting the hover
        '<b>Gross earned income</b>: $%{x:,.0f}' +
        '<br><b>Net earned income</b>: $%{y:,.0f}<extra></extra>', 
        
    ))

    ## Net final income view
    fig.add_trace(go.Bar(
        x = df['Gross earned income'],
        y = df['Net final income'],
        name = 'Net final income <br> (Net earned income <br>plus UBI)',
        marker_color = 'orange',
        hovertemplate = ## Formatting the hover
        '<b>Gross earned income</b>: $%{x:,.0f}' +
        '<br><b>Net final income</b>: $%{y:,.0f}<extra></extra>',
        
    ))

    ## UBI Benefit amount view
    fig.add_trace(go.Bar(
        x = df['Gross earned income'],
        y = df['UBI Benefit'],
        name = 'UBI <br> (Calculated at &#36;31K less 32.26&#37; <br> of gross earned income)',
        marker_color = 'green',
        base=df['Net earned income'],
        hovertemplate = ## Formatting the hover
        '<b>The calculated UBI entitlement</b>: $%{customdata:,.0f}<extra></extra>',
        customdata= ubi_benefit_hover_list

    ))

    ## Call out annotations on the chart
    fig.add_annotation(x= 0, y=35000,
    text="<b>Creating the income floor</b><br>If the individual receives <br> no employment income, they <br>  then receive the full UBI of  &#36;31k ",
    xanchor = "left", ## left/right for the annotation
    yanchor = "bottom", ## up/down for the annotation
    arrowhead = 0,
    arrowside = "end", ## arrow direction
    arrowcolor = "gray",
    ax = 8, ##arrow angle
    ay = -70, ##arrow length
    yshift=-3, ##text up and down
    bgcolor="rgb(255, 255, 240)", ##pale yellow colour
    showarrow=True,
    
        )

    fig.add_annotation(x= 95000, y=78000,
    text="<b> Medium to high earners unaffected</b><br>When gross earned income reaches $96,714, <br> the UBI is completely clawed back",
    xanchor = "right",
    arrowside = "end",
    arrowhead = 0,
    arrowcolor = "gray",
    ay = -15, ##arrow angle
    bgcolor="rgb(255, 255, 240)", ##pale yellow colour
    showarrow=True,
        )

    ## Figure formatting
    fig.update_layout(title='Annual UBI Income Effects', 
        title_y=0.95, ## Shift title position up and down
        title_x=0.03, ## Shift title position left and right
        barmode='group',
        xaxis_title='<b>Gross employment earned income &#36;', 
        yaxis_title = '<b>Income &#36; </b>',
        legend=dict(x=0.01, y=1.20, orientation='h', font=dict(size=13)), ## Format the legend position on the chart
        xaxis=dict(
            tickmode='linear',
            tick0=0,
            dtick=5000,
            tickfont=dict(size=14), ## font tick size
            range=[-2000,101000], ##negative a thousand so that 0K doesn't get chopped off on the chart
            title_font=dict(size=16),
            tickangle=-45
            ),

        yaxis=dict(
            tickmode='linear',
            dtick=20000,
            range=[0,100000],
            tickfont=dict(size=14),
            title_font=dict(size=16)
            ),
        
        margin=dict(l=90, r=30, t=100, b=80), ## Padding of the overal plot
        hoverlabel=dict(font_size=16), ## Hover font size
        title_font=dict(size=23), ## Title font size
        plot_bgcolor='rgb(255, 255, 240)', ## Pale yellow colour
        paper_bgcolor = 'rgb(255, 255, 240)', ## Pale yellow colour

        )
    
    fig.update_annotations(font_size=14)
    
    ### CHARTING ENDS ###

    ### BLURB BEGINS ###
    st.write("[Basic Income Australia Limited (BIA)](www.basicincomeaustralia.com) proposes a AU&#36;600/week (&#36;31,200/year) universal basic income (UBI) paid to every adult 18 years old and over in Australia without means testing, work requirements or conditions. The proposed amount aligns to the June Quarter 2023 single person Henderson Poverty Line of &#36;602.27/week¹, rounded down for modeling purposes.")
    st.write("The BIA policy recovers the UBI payment at 32.26 percent of an individual's gross salary up to &#36;96,714 which is approximately 1.4 times the median wage². The 32.26 percent clawback rate was chosen as it represents the dollar amount of annual UBI paid to an individual out of the &#36;96,714 per year threshold (32.26% = &#36;31,200/&#36;96,714).")
    st.write("This means a &#36;96,714 per annum salary is the threshold at which an individual ceases to be a net beneficiary. Hover your mouse on the chart below to explore the policy structure.")
    ## Fang in the chart
    st.plotly_chart(fig, use_container_width=True)

    st.write("If you earn more than &#36;96,714 a year, it means you will still receive the regular UBI payment like everyone else however the full UBI payment (&#36;31K) will be recovered after the fact through the group tax system.")
    st.write("If you earn less than &#36;96,714 a year, you become a net UBI beneficiary on a sliding scale. This means the more you earn, the lower the proportion of the $600/week UBI you will receive. The less you earn, the more of the UBI payment you get to keep. If you receive zero income in a year, you get to keep the full UBI amount (&#36;31K).")
    st.write("From an administrative perspective, you will receive &#36;600 into your bank account each week. Depending on your earnings that week, some or all of that basic income deposit will be repaid to the tax department. This will be done via your employer, or via the GST system or a special app that self-employed people can use to report their weekly earnings.") 
    st.write("If on any week your taxable income drops below &#36;1,860, you will end up with a net benefit. If you have no income that week, you’ll get to keep the whole &#36;600 to meet your basic needs in that week.  There will be no delay, need to apply or need to prove your entitlement.  Once you start earning again, the repayments will restart, based on your week's earnings. This system means you will receive the UBI unconditionally, while repayment will be conditional on the income you must report for tax purposes.  It adds no extra administration, while removing all mutual obligations.")
    st.write("Should this proposal be implemented, the policy intends to match the weekly payment rate to the Henderson Poverty Line and adjust the maximum income threshold to reflect the latest wage data.")
    st.write("For more details visit BIA's [policy page](https://basicincomeaustralia.com/policy/).")
    
    
    st.markdown("""<span style='font-size: 11px;'>¹[Melbourne Institute: Applied Economic & Social Research, Poverty Lines Australia - June Quarter 2023](https://melbourneinstitute.unimelb.edu.au/publications/poverty-lines)</span>""", unsafe_allow_html=True)
    st.markdown("""<span style='font-size: 11px;'>²[ABS - Employee earnings, reference period August 2023](https://www.abs.gov.au/statistics/labour/earnings-and-working-conditions/employee-earnings/latest-release )</span>""", unsafe_allow_html=True)

## CALCULATOR PAGE ##
with tab1:
## Set up the two columns

    ## Brief results
    netbenexpbrief = net_benefit_explainer_brief(annual_gross_income)

    ## Create a border
    netbenexpbrief = (
    "<div style='background-color: #f0f2f6; padding: 10px; border-radius: 10px;'>"
    + netbenexpbrief +
    "</div>"
    )
    
    ## 88888888 handles when the page first loads and there is no input
    if pi == 88888888:
        pass
    else:
        st.markdown(netbenexpbrief, unsafe_allow_html=True)
 
    ## Detailed results
    if pi == 88888888:
        pass

    else:
    # Padding
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("See calculation"):
        
            col1, col2 = st.columns(2)

            with col1:
                st.subheader('Current personal income taxation regime (no UBI)')
                st.write("Annual gross income:" , pi )
                st.write("Annual tax payable:" , int(annual_tax_payable) , "or" , round((annual_tax_payable/max(1,pi))*100,0) , "percent of your income")
                st.write("Annual net take home pay:" , int(annual_net_income))
                
            with col2:
                st.subheader("BIA's Proposed UBI mechanism")
                st.write("Annual gross income:" , pi )
                st.write("Annual tax payable:" , int(annual_tax_payable) , "or" , round((annual_tax_payable/max(1,pi))*100,0) , "percent of your income")
                ## preparing the clawback and recovery results for the markdown formatting so that the result formats look consistent
                clawback_result = int(clawback(annual_gross_income))
                recovery_explainer_result = ubi_recovery_explainer(annual_gross_income)
                st.markdown("UBI recovery amount: " + f"  <code>{clawback_result}</code>"+"(" + f"  <code>{recovery_explainer_result}</code>" + ")" , unsafe_allow_html=True)
                st.write("Net UBI:" ,  int(net_ubi_benefit) , "(" , int(clawback_amount), "-" , int(clawback(annual_gross_income)) ,")")
                st.write("Annual net take home pay + net UBI:" , int(net_benefit), "(" , annual_net_income , "+" , net_ubi_benefit, ")")
                netbenexpdetail = net_benefit_explainer_detailed(annual_gross_income)
                    ## Create a border
                netbenexpdetail = (
                "<div style='background-color: #f0f2f6; padding: 10px; border-radius: 10px;'>"
                + netbenexpdetail +
                "</div>"
                )

                st.markdown(netbenexpdetail, unsafe_allow_html=True)
            
            ## Padding
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(""" <span style="font-size: 8pt;">Tax calculations are based on the ATO 2023-2024 personal income tax schedule: https://www.ato.gov.au/rates/individual-income-tax-rates/</span>""", unsafe_allow_html=True)
            st.markdown(""" <span style="font-size: 8pt;">Note: This calculator does not cover any HECS-HELP repayments, Medicare levy, Medicare levy surcharge, working holiday makers' tax obligations nor the First Home Super Saver (FHSS) scheme. It simply models the latest Australian personal income tax structure assuming you were a full-year resident for tax purposes.</span>""", unsafe_allow_html=True)

## PROVIDE FEEDBACK PAGE ##
with tab3:
    # Custom CSS to set the font in the 'see calculation' expander
    custom_css2 = """
        <style>
        
        .form-container {
            display: flex;
            flex-wrap: wrap;
        }
        
        .wider-textarea {
            width: 100%;
            border: 1px solid #ccc; /* Thin border with light grey color */
            border-radius: 5px;
            padding: 5px;
        }

        .large-input {
            flex: 1;
            margin-bottom: 10px; /* Added margin-bottom */
            height: 40px; /* Adjust the height value as needed */
            border: 1px solid #ccc; /* Thin border with light grey color */
            border-radius: 5px;
            padding: 10px;
            width: calc(100% - 200px); /* Adjusted width to consider padding */
        }

    </style>
    """

    # Display the custom CSS
    st.markdown(custom_css2, unsafe_allow_html=True)

    st.markdown("""
        <h4>Please provide your feedback and ideas for improvements. Examples of other relevant calculators/tools are welcome.</h4>
        <form target="_blank" action="https://formsubmit.co/c2e828e64ff610d01976b3ed3b50ade0" method="POST">
            <div class="form-group">
                <input type="text" name="name" class="form-control large-input" placeholder="  Full Name" required>
            </div>
            <div class="form-group" style="margin-top: 10px;">
                <input type="email" name="email" class="form-control large-input" placeholder="  Email Address" required>
            </div>
            <div class="form-group" style="margin-top: 10px;">
                <textarea placeholder="  Your Message" class="form-control wider-textarea" name="message" rows="5" required></textarea>
            </div>
            <button type="submit" class="btn btn-lg btn-dark btn-block" style="margin-top: 10px;">Submit Form</button>
        </form>

    """, unsafe_allow_html=True)

st.markdown(""" <span style="font-size: 8pt;">Last updated 25 January 2024 | Calculator prepared by Jessica Chew | [jessicacychew.com](https://jessicacychew.com) | View the code on [GitHub](https://github.com/jessicacychew/bia_policy_model) </span> """, unsafe_allow_html=True)
## next steps (from 26 January 2024 onwards)
## Get feedback from people
## Do drop downs for weekly / monthly / annual views
## Dynamic input for UBI amount
## Population coverage estimate

