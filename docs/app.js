var app = angular.module('delegateApp', []);

app.controller('indexCtrl', function($scope, $http) {
    $scope.accounts = [];
    $scope.lastpayout = 0;
    $scope.nextpayout = 0;

    $http.get ('poollogs.json').then (function (res) {
        $scope.lastpayout = res.data.lastpayout * 1000;
        
        //sets the last payout weekly
        $scope.nextpayout = moment ($scope.lastpayout).add (1, 'week').valueOf();
        $scope.accounts = [];

        for (addr in res.data.accounts) {
            var it = res.data.accounts[addr];
            it['address'] = addr;
            $scope.accounts.push (it);
        }
    });

    //get the super representative delegate details
    $http.get ('http://localhost:9305/api/delegates/get?username=genesisDelegate1').then (function (res) {
        $scope.delegate = res.data.delegate;
    });
});
