# Python script to download Notion DB (35mm shots) and parse it into DataViz

## Import packages 
from notion_client import Client
from pprint import pprint
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import random

## Read token 
with open("credentials.txt", "r") as file:
    credentials = file.readlines()
    notion_token = credentials[0].strip() # first line is Token
    notion_db_id = credentials[1].strip() # second line is DB id

## Notion: read DB (data.frame) https://www.youtube.com/watch?v=rQeG6DeUPNs
client = Client(auth = notion_token) # set up authentication
db_info = client.databases.retrieve(database_id = notion_db_id) # read DB
pd.DataFrame.from_dict(db_info, orient = "index") # DB metadata

## define function to parse rows 
def safe_get(data, dot_chained_keys):
    keys = dot_chained_keys.split('.')
    for key in keys:
        try:
            if isinstance(data, list):
                data = data[int(key)]
            else:
                data = data[key]
        except (KeyError, TypeError, IndexError):
            return None
    return data

## extract rows to dictionary
db_rows = client.databases.query(database_id=notion_db_id)
db35mm = []
for row in db_rows['results']:
    roll = safe_get(row, 'properties.ID.title.0.plain_text')
    date = safe_get(row, 'properties.DateTaken.date.start')
    film = safe_get(row, "properties.Film.multi_select.0.name") 
    brand = safe_get(row, 'properties.Brand.multi_select.0.name')
    Type = safe_get(row, 'properties.Type.multi_select.0.name')
    iso = safe_get(row, 'properties.ISO.number')

    db35mm.append({
        'roll': roll,
        'date': date,
        'film': film,
        'brand': brand,
        'Type': Type, 
        'iso': iso
    })

## parse list to pandas DF
db35mm = pd.DataFrame.from_dict(db35mm)

## Convert DataFrame to HTML for report parsing
db35mm_html = db35mm.to_html(index=False)

## Prepare plots
### Film
#### define color
unique_film = db35mm["film"].unique() # get unique films
random_colors = {type_: f'#{random.randint(0, 0xFFFFFF):06x}' for type_ in unique_film} # get unique color per entry

#### Create a figure with two subplots side by side
fig, axs = plt.subplots(1, 2, figsize=(12, 6))

#### First plot: count of different films
film_counts = db35mm["film"].value_counts().sort_values()
film_counts.plot(kind='bar', ax=axs[0], color=[random_colors.get(i, "#7f7f7f") for i in film_counts.index])
axs[0].set_title("All the different films I've shot (Count)")
axs[0].set_ylabel("n")

#### Second plot: percentage of films
film_percentages = db35mm["film"].value_counts(normalize=True).sort_values() * 100
film_percentages.plot(kind='bar', ax=axs[1], color=[random_colors.get(i, "#7f7f7f") for i in film_percentages.index])
axs[1].set_title("All the different films I've shot (Percentage)")
axs[1].set_ylabel("Percentage")

#### Save the plot to a BytesIO object
img1 = BytesIO()
plt.savefig(img1, format='png')
plt.close()
img1.seek(0)

# Convert image to base64 string
img1_base64 = base64.b64encode(img1.getvalue()).decode('utf8')

### Brand
#### define color
unique_brand = db35mm["brand"].unique() # get unique brands
colors_brand = {
    "Rollei": "#820b03",
    "Kodak": "#e6a627",
    "Cinemot": "#279ce6",
    "Ilford": "#36015c",
    "Adox": "#ed8b4a",
    "Bergger": "#fa232a",
    "Cinestill": "#b35054",
    "Revelab": "#9c50b3",
    "Revelog": "#030002",
    "Dubblefilm": "#e874e4",
    "Fomapan": "#7a767a",
    "Lomography": "#472046",
    "Fujifilm":  "#045e1a",
}

#### Create a figure with two subplots side by side
fig, axs = plt.subplots(1, 2, figsize=(12, 6))

#### First plot: count of different brands
brands_counts = db35mm["brand"].value_counts().sort_values()
brands_counts.plot(kind='bar', ax=axs[0], color=[colors_brand.get(i, "#7f7f7f") for i in brands_counts.index])
axs[0].set_title("All the different brands I've shot (Count)")
axs[0].set_ylabel("n")

#### Second plot: percentage of brands
brand_percentages = db35mm["brand"].value_counts(normalize=True).sort_values() * 100
brand_percentages.plot(kind='bar', ax=axs[1], color=[colors_brand.get(i, "#7f7f7f") for i in brand_percentages.index])
axs[1].set_title("All the different brands I've shot (Percentage)")
axs[1].set_ylabel("Percentage")

#### Save the plot to a BytesIO object
img2 = BytesIO()
plt.savefig(img2, format='png')
plt.close()
img2.seek(0)

# Convert image to base64 string
img2_base64 = base64.b64encode(img2.getvalue()).decode('utf8')



# Create an HTML string with the embedded image
html_str = f"""
<html>
<head></head>
<body>
<h1>Data Table</h1>
{db35mm_html}
<h2>The film I shoot</h2>
<img src="data:image/png;base64,{img1_base64}" alt="The film I shoot">
<h3>The brands of the films</h3>
<img src="data:image/png;base64,{img2_base64}" alt="The brands of the films">
</body>
</html>
"""

# Write the HTML string to a file
with open("output.html", "w") as f:
    f.write(html_str)

print("HTML file created: output.html")











