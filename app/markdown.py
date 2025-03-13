

app_style = """
    <style>
    /* Adjust sidebar width 
    [data-testid="stSidebar"] {
        min-width: 400px;
        /* max-width: 600px; */
        
    }*/

    /* Center-align main content and adjust spacing */
    [data-testid="stAppViewContainer"] {
        padding-left: 10px;
        padding-right: 10px;
    }

    /* Style chat container */
    .custom-ai-content {
        background-color: #44475a; /* Dark background */
        padding: 10px; /* Inner padding */
        border-radius: 10px; /* Rounded corners */
        color: #f8f8f2; /* Light text color */
        font-size: 16px; /* Font size */
        font-family: 'Arial', sans-serif; /* Font family */
        box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.3); /* Subtle shadow */
        margin-bottom: 15px; /* Space below the container */
    }


    </style>
    """

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """

# Remove whitespace padding that is on top of the page
reomove_padding = """
        <style>
               .block-container {
                    padding-top: 0rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """