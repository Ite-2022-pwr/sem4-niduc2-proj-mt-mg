import time
from colorama import Style, Fore

class RandomNumberGenerator:
    __modulus: int | None = None
    __mnoznik: int | None = None
    __przyrost: int | None = None
    __seed: int | None = None
    __amount: int | None = None

    def __init__(self, modulus, amount):
        self.__modulus = modulus
        self.__mnoznik = 250
        self.__przyrost = 37
        self.__amount = amount
        self.__seed = self.generate_seed()

        #self.gen_number()

        #self.example()

        if self.check_values() == False:
            print(Fore.RED, "[-] Provided values are incorrect. Exiting...", Style.RESET_ALL)


    def generate_sequence(self):
        for i in range(self.__amount):
            r_tmp = 0
            print()


    def gen_number(self):
        r_previous = self.__seed
        val_tmp = (self.__mnoznik*r_previous + self.__przyrost) % self.__modulus
        u_val = (val_tmp/(self.__modulus-1))*self.__modulus
        

        return u_val


    def gen_numbers(self):
        tmp = 0
        values = []
        r_previous = self.__seed
        for i in range(self.__amount):
            val_tmp = (self.__mnoznik*r_previous + self.__przyrost) % self.__modulus
            u_val = (val_tmp/(self.__modulus-1))*self.__modulus
            #print(Fore.GREEN, f"R{i+1} = {self.__mnoznik * r_previous + 1} mod {self.__modulus} = {int(u_val)}", Style.RESET_ALL)
            
            values.append(int(u_val))        
    
            # print(int(u_val))
            r_previous = u_val
        return values

    def generate_seed(self) -> int:
        return int(time.time())
    
    def check_values(self) -> bool:
        if self.__mnoznik <= 0:
            False
        
        if self.__przyrost < 0:
            False
        
        if self.__modulus <= self.__przyrost:
            False

        if self.__modulus <= self.__seed:
            False

        True


if __name__ == '__main__':
    rng = RandomNumberGenerator(1000, 10000)
    #print (rng.gen_number())
    print(rng.gen_numbers())
