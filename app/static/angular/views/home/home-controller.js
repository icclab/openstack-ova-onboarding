"use strict";
angular.module('boarding.home', ['boarding.homeService', 'angularFileUpload', 'boarding.file'])
    .controller('HomeController', function ($scope, homeService) {
        $scope.openstack = homeService.getOpenstackDetails();
        $scope.ova = homeService.getOvaDetails();
        $scope.options = {
            availableOptions: ['import', 'export']
           };
        $scope.checkCredentials = function() {
            // Push to API, route to /home after

            homeService.sendOpenstackDetails($scope.openstack,'status').success(function(data) {
                console.log(data);

                $scope.status=data;
            });
        };
        $scope.pushToOpenstack = function() {
            // Push to API, route to /home after
            $scope.openstack['stack_name']=$scope.my_stack;
            var data = $scope.openstack;
            var file = $scope.myFile;
            console.log('file is ' );
            console.dir(file);
            
            homeService.sendOpenstackDetails(data,'upload', file).success(function(data) {
                console.log(data);
            });
        };

        $scope.downloadFromOpenstack = function() {
            // Push to API, route to /home after
            $scope.openstack['list_of_vms']=$scope.my_vms;
            var data = $scope.openstack;
            homeService.sendOpenstackDetails(data,'generate', null).success(function(data) {
                console.log(data);
            });
        };
   });