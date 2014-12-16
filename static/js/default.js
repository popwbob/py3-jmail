function jmail_onload()
{
    console.log('jmail_onload');
    macct_details = document.getElementById("macct-details");
    console.log(macct_details);
    details_li = macct_details.getElementsByTagName("li");
    for (i = 0; i < details_li.length; i++)
    {
        li_inputs = details_li[i].getElementsByTagName("input");
        for (j = 0; j < li_inputs.length; j++)
        {
            input = li_inputs[j];
            input.disabled = "disabled";
        }
    }
}

jmail_onload();
