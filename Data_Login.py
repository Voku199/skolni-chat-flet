import flet as ft  
from flet import *
import mysql.connector

# Connect
mydb = mysql.connector.connect(
   host="127.0.0.1",
    port=3306,
    user="root",
    password="root",
    database="chat"
)

cursor = mydb.cursor()



def main(page:Page):
    user_name = TextField(label="name")
    password = TextField(label="password")
    
    mydt = DataTable(
        columns=[
            DataColumn(Text("id")),
            DataColumn(Text("user_name")),
            DataColumn(Text("password")),
            DataColumn(Text("actions")),
		],
        rows=[]
     
		
    )
    
        #Ok
    def deletebtn(e):
        pass

    def editbtn(e):
        pass   
    
    
    def load_data():
        login_name = "voku"
        cursor.execute("SELECT * FROM user WHERE user_name = %s OR email = %s LIMIT 1", (login_name,login_name))
        result = cursor.fetchall()

        columns = [column[0] for column in cursor.description]
        rows = [dict(zip(columns, row)) for row in result]

        for row in rows:
            print(row)
            mydt.rows.append(
                DataRow(
                    cells=[
                        DataCell(Text(row["id"])), #Pak to zkopíruj
                        DataCell(Text(row["user_name"])), #Pak to zkopíruj
                        DataCell(Text(row["password"])), #Pak to zkopíruj
                        DataCell(
                            Row([
                            IconButton("delete",icon_color="red",
                                    data=row,
                                    on_click=deletebtn
                                    ),
                        IconButton("create",icon_color="green",
                                    data=row,
                                    on_click=editbtn
                                    ),           
                            ]
                                

                            )
                        )

                        

                    ]
                    
                )
            )
        page.update()  

    #Ok
    load_data()             

    def addtodb(e):
        try:
            sql = "INSERT INTO user (user_name,password) VALUES(%s,%s)"
            val = (user_name.value, password.value)
            cursor.execute(sql,val)
            mydb.commit()
            print(cursor.rowcount,"YOUR RECORD INSERT !!")
            
			#Ah sh*t here we again GTA san adnreas
            mydt.rows.clear()
            load_data()

            page.snack_bar = SnackBar(
                Text("Data success add", size=20),
                bgcolor="green"
            )
            page.snack_bar.open = True 
            page.update()

        except Exception as e:
            print(e)
            print("error")

    # nametxt.value = "aa"
    # user_nametxt.value = "a"
    page.update()

			
        
	
    page.add(
    Column([
        user_name,
        password,
        ElevatedButton("add to db",
            on_click=addtodb           
			),
         mydt   

	    ]))
        

    

ft.app(target=main)