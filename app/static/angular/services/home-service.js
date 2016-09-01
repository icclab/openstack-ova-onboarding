"use strict";
angular.module('boarding.homeService', [])
    .service('homeService', function ($http) {

        var openstack = null
        var ova = null

        this.getOpenstackDetails = function() {
            // get current receipt or one specified by id
            return openstack;
        };
        this.getOvaDetails = function() {
            // get current receipt or one specified by id
            return ova;
        };
        this.sendOpenstackDetails = function(openstack, method) {
            var methodForRequest = "POST";
            var url = '/api/' + method;
            var promise = $http({method: methodForRequest, url: url, data: openstack})
                .error(function() {
                    console.log("something wrong happened ");
                });
            return promise;
        };
        
        this.uploadFileToUrl = function(file, uploadUrl){
            var fd = new FormData();
            fd.append('file', file);
            $http.post(uploadUrl, fd, {
                    transformRequest: angular.identity,
                    headers: {'Content-Type': undefined}
                })
                .success(function(){
                })
                .error(function(){
                });
        }
    });