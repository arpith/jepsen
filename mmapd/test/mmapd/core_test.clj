(ns mmapd.core-test
  (:require [clojure.test :refer :all]
	[jepsen.core :as jepsen]
            [mmapd.core :refer :all]))

(deftest a-test
  (testing "running mmapd-test"
    (is (:valid? (:results (jepsen/run! (mmapd-test "3.4.5+dfsg-2")))))))
