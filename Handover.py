import numpy as np
import random
import matplotlib.pyplot as plt
from copy import deepcopy

#==============================#Parameter Settings#==============================================================================================#
class HandoverProgram:

    def __init__(self):
        # self.bs_EIRP = int(input("Enter the Base Station EIRP: "))
        # self.bs_distance_sc = (1000* int(input("Enter the Base Station distance from small cell in km: ")))
        self.bs_EIRP = 57
        self.bs_distance_sc = 3000
        self.sc_EIRP = 30  # Small cell EIRP
        self.rsl_threshold = -102  # Mobile RX Threshold
        self.channels_bs = 30   # Channels vailable at Base Sation
        self.channels_sc = 30  # Channels available at Small cell
        self.Total_number_of_call_attempts = 0
        self.number_of_call_attempts_sc = 0  # Toal number of call attempts at small cell
        self.number_of_call_attempts_bs = 0  # Toal number of call attempts at small cell
        self.number_of_successful_call_connections_sc = 0   # Total number of successful call connections at Small cell
        self.number_of_successful_call_connections_bs = 0   # Total number of successful call connections at Base Station
        self.call_block_count_capacity_bs = 0   # call block due to capacity at Base Station
        self.call_block_count_capacity_sc = 0  # call block due to capacity at Small Cell
        self.call_block_count_power_bs = 0  # call block due to power at Base Station
        self.call_block_count_power_sc = 0  # call block due to power at Small cell
        self.call_drop_bs = 0  # Total call drops at Base station
        self.call_drop_sc = 0  # Total call drops at Small cell
        self.successful_call_completion_bs = 0  # Successful call completion at Base Station
        self.successful_call_completion_sc = 0  # Successful call completion at Small cell
        self.HO_attemp_SC_to_BS = 0  ##Handover attempt from Small cell to Base Station
        self.HO_attemp_BS_to_SC = 0  ##Handover attempt from Base Station to Small cell
        self.HO_success_SC_to_BS = 0  ##Handover success from Small cell to Base Station
        self.HO_success_BS_to_SC = 0  ##Handover success from Small cell to Base Station
        self.HO_failure_SC_to_BS = 0  ##Handover failure from Small cell to Base Station
        self.HO_failure_BS_to_SC = 0  ##Handover failure from Small cell to Base Station
        self.total_active_calls_bs = 0  ##active calls at Base Station
        self.total_active_calls_sc = 0  ##active calls at Small cell
        # user_currently_latched_to = ''  ##active calls at Small cell
        self.user_parameter_dictonary = {}  ##create a blank disctonary to store user data such as call duration, distance etc.
        self.output_summary_at_time_list = [3600, 7200, 10800, 14400]  ##Output required at this times
        self.shadowing_list = (np.random.normal(0,2,500))   #create 500 shadowing values list for every 10m

#==============================#Functions#==========================================================================================================#

    def fading(self):
        "Function to calculate fading using Rayleigh distribution"
        
        rayleigh_dist_values = np.random.rayleigh(1,10)
        rayleigh_dist_values_dB= np.sort(20* np.log10(rayleigh_dist_values))
        return(rayleigh_dist_values_dB[1])

#==================================================================================================================================================

    def Oka_Hata(self, distance, height):
        "Function to calculate propagation loss using Okamura-Hata model"

        pathloss = 69.55 + 26.16*np.log10(1000) - 13.82*np.log10(height) + ((44.9 - 6.55*np.log10(height))*np.log10(distance/1000))- ((1.1*np.log10(1000) - 0.7)*1.7) + (1.56*np.log10(1000)-0.8)
        return pathloss

#==================================================================================================================================================

    def rsl_base_station(self, distance_inp):
        "Function to calculate RSL from base station"


        distance = self.bs_distance_sc - distance_inp  #calculate distance from base station

        height_bs = 50
        if (self.bs_distance_sc - 200) <= distance <= (self.bs_distance_sc - 190):  #if user in door lobby
            a = distance-(self.bs_distance_sc - 200)  #distance from parking lot
            b= 10-a  ##distance from interior of mall
            penetration_loss_base_station = 21*(a/10)  #interpolation for penetration loss
            total_path_loss = self.Oka_Hata(distance,height_bs)+ penetration_loss_base_station  #calculate path loss
            rsl = self.bs_EIRP - total_path_loss  + self.fading() +  (distance)  #calculate RSL
            return rsl  #return RSL
        elif distance > (self.bs_distance_sc - 190):  #if user in mall
            total_path_loss = self.Oka_Hata(distance,height_bs) + 21 #calculate path loss

            rsl = self.bs_EIRP - total_path_loss+ self.fading() + self.shadowing(distance) #calculate RSL
            return rsl  #return RSL
        else:   #if user on road
            total_path_loss = self.Oka_Hata(distance,height_bs) + self.fading() #calculate path loss
            rsl = self.bs_EIRP - total_path_loss + self.fading() + self.shadowing(distance) #calculate RSL
            return rsl  #return RSL

#==================================================================================================================================================
  
    def shadowing(self, distance):
        "Function to calculate shadowing"
        shadowing_list = (np.random.normal(0,2,500))
        index = int(distance/10)  #find index with respect to a distance to access the list
        return self.shadowing_list[index]

#==================================================================================================================================================

    def rsl_small_cell(self, distance):
        "Function to calculate RSL from small cell"
        
        height_sc= 10
        if 190<=distance<=200:
            a = 200-distance  #distance from parking lot
            b= 10-a  ##distance from interior of mall
            penetration_loss_small_cell = 21*(b/10)  #interpolation for penetration loss
            total_path_loss = self.Oka_Hata(distance, height_sc)  + penetration_loss_small_cell  #calculate path loss
            rsl = self.sc_EIRP - total_path_loss + self.fading()  #calculate RSL
            return rsl  #return RSL
        elif distance < 190:
            total_path_loss = self.Oka_Hata(distance, height_sc)  #calculate path loss
            rsl = self.sc_EIRP - total_path_loss + self.fading()  #calculate RSL
            return rsl  #return RSL
        else:
            total_path_loss = self.Oka_Hata(distance, height_sc) + 21  #calculate path loss
            rsl = self.sc_EIRP - total_path_loss + self.fading()  #calculate RSL
            return rsl  #return RSL
    
#==================================================================================================================================================

    def call_duration(self):
        "Function to find out random call duration"
        
        user_call_duration = int(np.random.exponential(scale= 180))  #select a call duration from exponential distribution with mean = average call duraion
        if user_call_duration != 0:
            return user_call_duration   

#==================================================================================================================================================

    def user_to_del_from_dictonary(self, user_id):
        "Function to delete a user data(key) from user database dictonary"

        if user_id in self.user_parameter_dictonary.keys():   #check if that user id is in active call dictonary
            local_self_user_parameter_dictonary = deepcopy(self.user_parameter_dictonary) #make a deepcopy of the userdictonary for deletion of a key
            del local_self_user_parameter_dictonary[user_id]  #delete a perticular key(user data)
            self.user_parameter_dictonary = local_self_user_parameter_dictonary  #assign the copied dictonary yo original dictonary

#==================================================================================================================================================

    def user_data_monitoring(self, user_id):
        "Function to monitor user data evry second such as call duration and distance"

        user_call_duration = self.user_parameter_dictonary[user_id][1]  #get the call duration for perticular user(key)
        user_distance = self.user_parameter_dictonary[user_id][2]  #get the distance for perticular user(key)
        user_direction_motion = self.user_parameter_dictonary[user_id][0]  #get the direction of motion for perticular user(key)

        if user_call_duration != None:
            self.user_parameter_dictonary[user_id][1] = user_call_duration - 1   #reduce the call duration by 1 second
        
        if  1 < user_distance <= 200:    #if user in mall
            if user_direction_motion == 0: #moving towards smallcell
                self.user_parameter_dictonary[user_id][2] = user_distance - 1  #reduce the user distance by 1
            elif user_direction_motion == 1: #moving towards base station
                self.user_parameter_dictonary[user_id][2] = user_distance + 1  #increase the user distance by 1 

        elif 200 < user_distance <= 300: 
            if user_direction_motion == 0: #moving towards smallcell
                self.user_parameter_dictonary[user_id][2] = user_distance - 1  #reduce the user distance by 1
            elif user_direction_motion == 1: #moving towards base station
                self.user_parameter_dictonary[user_id][2] = user_distance + 1  #increase the user distance by 1

        elif 300 < user_distance <= (self.bs_distance_sc - 1):
            if user_direction_motion == 0: #moving towards smallcell
                self.user_parameter_dictonary[user_id][2] = user_distance - 15  #reduce the user distance by 1
            elif user_direction_motion == 1: #moving towards base station
                self.user_parameter_dictonary[user_id][2] = user_distance + 15   #increase the user distance by 1 

#==================================================================================================================================================

    def call_status_update(self, user_id):
        "Function to monitor user data evry second such as call duration and distance"
        
        user_call_duration = self.user_parameter_dictonary[user_id][1]  #get the call duration for perticular user(key)
        user_currently_latched_to = self.user_parameter_dictonary[user_id][3]  #find out to which the user is currently latched to
        user_distance = self.user_parameter_dictonary[user_id][2]  #get the distance for perticular user(key)


        
        if user_call_duration != None:
            if user_call_duration <= 0:  #if call duration less than or equal to zero, call completion success
                if user_currently_latched_to == 'Small Cell': #check if it is latched to small cell
                    self.channels_sc += 1  #increase the channels in small cell
                    self.user_to_del_from_dictonary(user_id) #delete that user from the dictonary
                    self.successful_call_completion_sc += 1 #count it as successful call completion a small cell
                    
                elif user_currently_latched_to == 'Base Station':  #check if it is latched to base station
                    self.successful_call_completion_bs += 1 #count it as successfu call completion on base station
                    self.channels_bs += 1  #free up the channel at base station
                    self.user_to_del_from_dictonary(user_id) #delete the user from the dictonary

                
        if user_distance > (self.bs_distance_sc - 1) or user_distance < 1:    #if the user is within 1 meter or went pass the BS and SC, call successful completion
            if user_currently_latched_to == 'Small Cell': #check if it is latched to small cell
                self.successful_call_completion_sc += 1 #count it as successfu call completion on base station
                self.channels_sc += 1 #free up the channel at base station
                self.user_to_del_from_dictonary(user_id) #delete the user from dictonary


            elif user_currently_latched_to == 'Base Station':   #check if it is latched to base station
                self.successful_call_completion_bs += 1#count it as successfu call completion on base station
                self.channels_bs += 1 #free up the channel at base station
                self.user_to_del_from_dictonary(user_id) #delete the user from the dictonary

#==================================================================================================================================================

    def call_drop_Handover_check(self, user_id):
        "Function to check for call drop possibility and handover, every second"
        
        user_dist = self.user_parameter_dictonary[user_id][2] #get the user distance from the database        
        user_currently_latched_to = self.user_parameter_dictonary[user_id][3] #find out to which user is latched

        if user_dist != None:  #check if the distance is not None
            RSL_basestation = self.rsl_base_station(user_dist) #calculate the RSL from base station
            RSL_smallcell = self.rsl_small_cell(user_dist) #calculate RSL from small cell


        if user_currently_latched_to == 'Base Station': #if user latched to base station then go inside
            if RSL_basestation  < self.rsl_threshold:  #check if the RSL is worst than -102 threshold
                self.call_drop_bs += 1  # count it as call drop
                self.user_to_del_from_dictonary(user_id) #delete user from the dictonary
                self.channels_bs += 1  #free up the channel from BS
                
            elif RSL_basestation  >= self.rsl_threshold: #if RSL of BS is above threshold then 
                if RSL_smallcell > RSL_basestation: #check if RSL of SC above RSL BS
                    self.HO_attemp_BS_to_SC += 1 #count it as a handover attempt from bs to sc
                    if 1<= self.channels_sc <= 30: #check if the channel available at sc
                        self.HO_success_BS_to_SC += 1 #count it as handover success
                        self.user_parameter_dictonary[user_id][3] = 'Small Cell' #change the entity to which it is currently latched to
                        self.channels_bs += 1  #free up the channel
                        self.channels_sc -= 1  #assign the channel 
                    else:
                        self.HO_failure_BS_to_SC += 1  #count it as handover failure
                        self.call_block_count_capacity_sc += 1 #count it as call block due to capacity as sc
                        
        elif user_currently_latched_to == 'Small Cell':  #if user latched to SC then go inside
            if RSL_smallcell < self.rsl_threshold: #check if the RSL SC is poor than -102
                self.call_drop_sc += 1  #count it as a call drop
                self.user_to_del_from_dictonary(user_id)  #delete the user from the dictonary
                self.channels_sc += 1  #free up the channel at SC
                
            elif RSL_smallcell  >= self.rsl_threshold: #check if the RSL SC is greater than RSL threshold
                if RSL_basestation > RSL_smallcell: #check if the RSL BS is greater than RSL small cell
                    self.HO_attemp_SC_to_BS += 1  #count it as handover from SC to BS
                    if 1<= self.channels_bs <= 30 : #check if the channel available at BS
                        self.HO_success_SC_to_BS += 1 #count it as HO success as channel available
                        self.user_parameter_dictonary[user_id][3] = 'Base Station' #change the entity to which it is currently latched to
                        self.channels_sc += 1 #free up the channel at SC
                        self.channels_bs -= 1 #reduce the channel at BS
                    else:
                        self.HO_failure_SC_to_BS += 1 #if channel not available then handover failre
                        self.call_block_count_capacity_bs += 1 #count it as a call block due to capacity              
            
#==================================================================================================================================================

    def user_id_list_update(self, dist, velocity, site):

        if site == 'Small Cell':
            self.channels_sc -= 1
            self.number_of_successful_call_connections_sc += 1
        else: 
            self.channels_bs -= 1
            self.number_of_successful_call_connections_bs += 1

        return [velocity, self.call_duration(), dist, site]


#==============================#Main Program#==========================================================================================================#
    
    def main(self):
        for time in range(1,14401):
            #print('timer = {}'.format(time))
            self.total_active_calls_sc = 0  #initialize the active calls counter to zero
            self.total_active_calls_bs = 0  #initialize the active calls counter to zero                            
            user_who_can_make_call = 1000 - len(self.user_parameter_dictonary.keys()) #find out how many of the users available to make call
            total_active_calls_list = [] #create a black list of active calls

            for key, value in self.user_parameter_dictonary.items():
                    total_active_calls_list.append(value[3]) #append the user latched to parameter in alist
            
            for j in total_active_calls_list: 
                if j == 'Small Cell':
                    self.total_active_calls_sc = self.total_active_calls_sc + 1 #count the users latched to small cell
                elif j == 'Base Station':
                    self.total_active_calls_bs = self.total_active_calls_bs + 1 #count the users latched to base station
                else:
                    break
                    
            self.channels_sc = 30 - self.total_active_calls_sc  #find out the current channel availability
            self.channels_bs = 30 - self.total_active_calls_bs  #find out the current channel availability
            
            x = np.random.random(user_who_can_make_call)  #Generate random numbers for users between 0 to 1
            x.sort() #sort the list
            test_list = [] #create a black list
            for num in x: 
                if num <= (1/3600): #check if the user can make a call or not
                    test_list.append(num) #append the number of users who call make call
                    
            for users in test_list:
                user_id = np.random.randint(1, 1000)  #Select a random number between 1 to 1000 and take it as a user ID   
                if user_id in self.user_parameter_dictonary.keys():  #Check if that user is already in active call or not
                    continue  #if user already in call, continue to next user
                user_id_list = []  #create a black list to store the user data such as call duration , distance, direction and to whcih it is latched to
                self.Total_number_of_call_attempts += 1 #count it as a call attmp

    #=================================================================================================================================================

                user = np.random.random()  #generate a random probalility number for a user
                if user >= 0.5:  #condition to check if user in mall
                    #user in mall

                    distance = np.random.random()*200  #generate random number to calculate user distance in mall from small cell
                      
                    RSL_basestation = self.rsl_base_station(distance)  #Calculate RSL with respect to Base Station
                    RSL_smallcell = self.rsl_small_cell(distance)  #Calculate RSL with respect to Small cell
                    self.number_of_call_attempts_sc += 1 #count it as a call attempt on SC
                    
                    if RSL_smallcell >= self.rsl_threshold:  #Check if the RSL is above mobile RSL threshold
                        if 1 <= self.channels_sc <= 30:  #cheack the availability of channels at small cell
                            
                            user_id_list = self.user_id_list_update(distance, 1, 'Small Cell')

                        else:
                            self.call_block_count_capacity_sc += 1  #call blcked as the channels are not available at small cell
                            
                            if RSL_basestation >= self.rsl_threshold:  #check if base station can pick that user as per RSL
                                if 1 <= self.channels_bs <= 30:  #check the channel availability at base station
                                    
                                    user_id_list = self.user_id_list_update(distance, 1, 'Base Station')
                                                             
                                else:
                                    self.call_drop_sc += 1 #count it as a call drop
                            else:
                                self.call_drop_sc += 1  #count it a call drop
                                              
                    else:
                        self.call_block_count_power_sc += 1  #count it as a call block due to power
                        
                        if RSL_basestation >= self.rsl_threshold:  #check if RSL BS greater than RSL threshold
                            if 1 <= self.channels_bs <= 30:
                                user_id_list = self.user_id_list_update(distance, 1, 'Base Station')

                            else:
                                self.call_drop_sc += 1 #count as a call drop
                        else:
                            self.call_drop_sc += 1 #count as a call drop

    #==================================================================================================================================================            
                    
                elif 0.3 <= user < 0.5: #condition to check if user in parking lot
                    #user in parking lot
                    
                    distance = np.random.random()*100 + 200 #generate random number to find the user's distance in parking lot
                    
                    RSL_basestation = self.rsl_base_station(distance) #calculate the RSL from base station
                    RSL_smallcell = self.rsl_small_cell(distance) #calculate the RSL from small cell
                    self.number_of_call_attempts_bs += 1 #count it as a call attemp on BS

                    if RSL_basestation >= self.rsl_threshold:  #check if the RSL BS is greater than -102
                        if 1 <= self.channels_bs <= 30: #check channel availability on BS
                            user_id_list = self.user_id_list_update(distance, 0, 'Base Station')
                            
                        else:
                            self.call_block_count_capacity_bs += 1 #increase the call block counter
                            
                            if RSL_smallcell >= self.rsl_threshold: #check if RSL of SC greater than -102
                                if 1 <= self.channels_sc <= 30: #check channel availability
                                    user_id_list = self.user_id_list_update(distance, 0, 'Small Cell')

                                else:
                                    self.call_drop_bs += 1 #count it as a call drop on BS
                            else:
                                self.call_drop_bs += 1 #count it as a call drop on BS
                                              
                    else:
                        self.call_block_count_power_bs += 1  #count it as a call BLOCK on BS due to power
                        
                        if RSL_smallcell >= self.rsl_threshold: #check if RSL SC graeter than -102
                            if 1 <= self.channels_sc <= 30 : #check the channel availability
                                user_id_list = self.user_id_list_update(distance, 0, 'Small Cell')
                                
                            else:
                                self.call_drop_bs += 1 #count it as a call drop on BS
                        else:
                            self.call_drop_bs += 1  #count it as a call drop on BS


        #==================================================================================================================================================

                else :#user on road
                    
                    
                    distance = np.random.random()*((self.bs_distance_sc - 300)) + 300 #generate random number to find the users distance on the road

                    RSL_basestation = self.rsl_base_station(distance)  #calculate the RSL from BS
                    RSL_smallcell = self.rsl_small_cell(distance) #cal culate the RSL from SC
                    self.number_of_call_attempts_bs += 1  #increase the call attempt counter at BS

                    if RSL_basestation >= self.rsl_threshold:  #check if the RSL BS is greater than -102
                        if 1 <= self.channels_bs <= 30: #check the channel abailability
                            user_id_list = self.user_id_list_update(distance, 0, 'Base Station')

                        else:
                            self.call_block_count_capacity_bs += 1 #count it as a call block due to capacity at BS
                            
                            if RSL_smallcell >= self.rsl_threshold: # check if RSL of SC is grater than -102
                                if 1 <= self.channels_sc <= 30 : #check the channel availability
                                    user_id_list = self.user_id_list_update(distance, 0, 'Small Cell')
                                    
                                else:
                                    self.call_drop_bs += 1  #call drop at BS
                            else:
                                self.call_drop_bs += 1  #call drop at BS
                                              
                    else:
                        self.call_block_count_power_bs += 1 #count it as a call blcok due to poer at BS
                        
                        if RSL_smallcell >= self.rsl_threshold:  # check if RSL of SC is grater than -102
                            if 1 <= self.channels_sc <= 30 :  #check the channel availability
                                user_id_list = self.user_id_list_update(distance, 0, 'Small Cell')

                            else:
                                self.call_drop_bs += 1   #call drop at BS
                        else:
                            self.call_drop_bs += 1   #call drop at BS

                if user_id_list != []:             
                    self.user_parameter_dictonary[user_id] = user_id_list  #append the user list in the disctory for a perticular key(user)
                    #print(self.user_parameter_dictonary)
                    


        #============Below code to monitor user data evry second and update the dictonary#==================================================================#

            active_users = self.user_parameter_dictonary.keys()  #create a list of users/ keys currently present in the dictonary
            for user_id in active_users:  #for a user in a active user list
                self.user_data_monitoring(user_id) #call the user monitoring function
                self.call_status_update(user_id) #call the function to update the call status

                if user_id in self.user_parameter_dictonary.keys():  # check if the user id in current dictonary
                    self.call_drop_Handover_check(user_id) #call the function of to check the call drop and handover


        #============Below code to print output after every hour#=========================================================================================#

            if time in self.output_summary_at_time_list:  #generate the output at evry hour
                        
                print('Output after {} hour of simulation :-' .format (time/3600))
                print('Base Station EIRP = {} and distance between Base Station and Small Cell = {}m'.format(self.bs_EIRP, self.bs_distance_sc))
                print("=========================================================================")
                print("=========================================================================")

                print('The number of channels currently in use at BS = {}'.format(self.channels_bs))
                print('The number of channels currently in use at SC = {}'.format(self.channels_sc))
                print('Current active calls in user dictionary = {}'.format(len(self.user_parameter_dictonary.keys())))

                print("=========================================================================")   

                print('Total number of call attempts = {}'.format(self.Total_number_of_call_attempts))
                print('The number of call attempts at Small cell = {}'.format(self.number_of_call_attempts_sc))
                print('The number of call attempts at Base Station= {}'.format(self.number_of_call_attempts_bs))

                print("=========================================================================")

                print('Total number of successful call connections (BS + SC) = {}'.format(self.number_of_successful_call_connections_bs + self.number_of_successful_call_connections_sc))
                print('The number of successful call connections at Small cell = {}'.format(self.number_of_successful_call_connections_sc))
                print('The number of successful call connections at Base Station = {}'.format(self.number_of_successful_call_connections_bs))

                print("=========================================================================")

                print('Total number of successfully completed calls (BS + SC) = {}'.format(self.successful_call_completion_sc + self.successful_call_completion_bs))
                print('The number of successfully completed calls at Small Cell = {}'.format(self.successful_call_completion_sc))
                print('The number of successfully completed calls at Base Station = {}'.format(self.successful_call_completion_bs))

                print("=========================================================================")

                print('Handover attempt from Small cell to Base Station = {}'.format(self.HO_attemp_SC_to_BS))
                print('Handover success from Small cell to Base Station= {}'.format(self.HO_success_SC_to_BS))
                print('Handover failure from Small cell to Base Station = {}'.format(self.HO_failure_SC_to_BS))
                print('Handover attempt from Base Station to Small cell= {}'.format(self.HO_attemp_BS_to_SC))
                
                print('Handover Success from Base Station to Small cell = {}'.format(self.HO_success_BS_to_SC))
                
                print('Handover failure from Base Station to Small cell = {}'.format(self.HO_failure_BS_to_SC))
                print("=========================================================================")

                print('Total number of call drops ( BS+ SC) = {}'.format(self.call_drop_sc + self.call_drop_bs))
                print('The number of call drops at Small Cell = {}'.format(self.call_drop_sc))
                print('The number of call drops at Base Station = {}'.format(self.call_drop_bs))
                
                print("=========================================================================")   

                print('Total number of call blocked due to signal strength (BS+ SC)  = {}'.format(self.call_block_count_power_sc + self.call_block_count_power_bs))
                print('The number of call blocked due to signal strength at Base Station = {}'.format(self.call_block_count_power_bs))
                print('The number of call blocked due to signal strength at Small Cell = {}'.format(self.call_block_count_power_sc))
                print ()
                print('Total number of call blocked due to capacity (BS+ SC)  = {}'.format(self.call_block_count_capacity_bs + self.call_block_count_capacity_sc))
                print('The number of call blocked due to capacity at Base Station = {}'.format(self.call_block_count_capacity_bs))

                print('The number of call blocked due to capacity at Small Cell = {}'.format(self.call_block_count_capacity_sc))

                print("=========================================================================")
                print("=========================================================================")
                print("=========================================================================")

        #================Below code for plotting the graph of RSL vs Distance=============================================================================#

        if self.bs_EIRP == 57: 
            rsl_sc_list=[]  #create a empty list for storing the RSL values from SC
            rsl_bs_list =[]  #create a empty list for storing the RSL values from BS
            plt.figure()  #create a figure
            plt.title('RSL vs Distance')   #assign a title to the plot
            for i in np.arange(1, 3000):  #generate the for loop for every meter up to 3km
                rsl_bs_list.append(self.rsl_base_station(i))  #append the RSL at distance from BS in the list
                rsl_sc_list.append(self.rsl_small_cell(i))   #append the RSL at distance from SC in the list
            plt.plot(np.arange(1, 3000, 1), rsl_bs_list,'b', label="BS_RSL")  #plot the rsl from BS
            plt.plot(np.arange(1, 3000, 1), rsl_sc_list,'r', label="SC_RSL")  #plot the rsl from SC
            leg = plt.legend(loc='upper right')  #shoe the legends
            plt.xlim(xmin=1, xmax = 2999)  #set the limits to x axis
            plt.ylabel('Received Signal Strength(dBm)')  #set the label to Y axis
            plt.xlabel('Distance(m)')  #set the label to X axis
            plt.xticks(np.arange(1,3000, step=100))  #set the x axis as per desired range
            plt.show()  #show the graph

if __name__ == '__main__':
    ob = HandoverProgram()
    ob.main()