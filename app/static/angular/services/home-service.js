"use strict";
angular.module('boarding.homeService', ['angular-loading-bar', 'ngAnimate'])
    .service('homeService', function ($http, cfpLoadingBar) {

        var openstack = null;
        var ova = null;

        this.getOpenstackDetails = function() {
            // get current receipt or one specified by id
            return openstack;
        };
        this.getOvaDetails = function() {
            // get current receipt or one specified by id
            return ova;
        };
        this.sendOpenstackDetails = function(openstack, method, file) {
            var url = '/api/' + method;
            var fd = new FormData();
            cfpLoadingBar.start();
            fd.append('username', openstack.username);
            fd.append('password', openstack.password);
            fd.append('project_id', openstack.project_id);
            fd.append('region', openstack.region);
            fd.append('url', openstack.url);
            fd.append('stack_name', openstack.stack_name);
            fd.append('method', openstack.method);
            fd.append('file', file);

            var array_vms = String(openstack.list_of_vms).split(", ");
            if(typeof openstack.list_of_vms !== "undefined"){
            for (var i = 0; i < array_vms.length; i++) {
                fd.append('instance_id', array_vms[i]);
                }
                }

            var promise = $http.post(url, fd, {
                    transformRequest: angular.identity,
                    headers: {'Content-Type': undefined}
                })
                .error(function() {
                    console.log(promise);
                });
            cfpLoadingBar.complete();
            return promise;
        };

    });