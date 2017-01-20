'use strict';

/* App Module */

var boarding = angular.module('boarding', [
    'ngRoute',
    'angularFileUpload',
    'boarding.navbar',
    'boarding.home'
]);

boarding.config(['$routeProvider',
  function($routeProvider) {
    $routeProvider
        .when('/about', {
        templateUrl: 'angular/views/about/about.html'
      })
        .when('/home', {
        templateUrl: 'angular/views/home/home.html',
        controller: 'HomeController'
      })
        .otherwise({
        redirectTo: '/home'
      });
  }]);
