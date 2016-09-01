"use strict";
angular.module('boarding.home', ['boarding.homeService', 'angularFileUpload', 'boarding.file'])
    .controller('HomeController', function ($scope, homeService) {
        $scope.openstack = homeService.getOpenstackDetails();
        $scope.ova = homeService.getOvaDetails();
        $scope.checkCredentials = function() {
            // Push to API, route to /home after
            homeService.sendOpenstackDetails($scope.openstack,'status').success(function(data) {
                console.log(data);
                var credentials_status= false;
                if (data.nova_status && data.glance_status && data.heat_status){
                    credentials_status= true
                }
                $scope.status={credentials: credentials_status};
            });
        };
        $scope.pushToOpenstack = function() {
            // Push to API, route to /home after
            $scope.openstack['ova_file']=$scope.myFile.name;
            $scope.openstack['stack_name']=$scope.my_stack;
            $scope.uploadFile();
            var data = $scope.openstack
            
            homeService.sendOpenstackDetails(data,'upload').success(function(data) {
                console.log(data);
            });
        };
        $scope.uploadFile = function(){
            var file = $scope.myFile;

            console.log('file is ' );
            console.dir(file);
            var uploadUrl = "/api/file/upload";
            homeService.uploadFileToUrl(file, uploadUrl);
        };

   });