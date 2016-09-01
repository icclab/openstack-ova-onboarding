"use strict";
angular.module('boarding.navbar', [])
    .controller('NavbarController', function ($scope, $location) {
        $scope.isActive = function (viewLocation) {
            return viewLocation = $location.path();

        };

    });
