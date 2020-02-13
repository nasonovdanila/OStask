import vk_api

class Vk:
    vkSes = 0

    def Vk_start(self,login,password):
        self.vkSes = vk_api.VkApi(login,password)
        self.vkSes.auth()
        vk = self.vkSes.get_api()
        if vk:
            print("All good")
        else:
            print("Shit")
        pass
    
    def Vk_get_fullname(self):
        vkinf = self.vkSes.method("account.getProfileInfo")
        bday = vkinf['bdate'].split(".") [2]
        if (int) (bday) == 2001:
            print(vkinf['last_name'] + " " + vkinf['first_name'] + " is born " + vkinf['bdate'])
        elif (int) (bday) == 1999:
            print("He is lie")


test = Vk()
login = input("Enter login : ")
passw = input("Enter pass : ")
test.Vk_start(login, passw)

test.Vk_get_fullname()
