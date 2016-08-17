(ns mmapd.core-test
  (:require [clojure.test :refer :all]
	[jepsen.core :as jepsen]
            [mmapd.core :refer :all]))

(deftest a-test
  (testing "FIXME, I fail."
(is (:valid? (:results (jepsen/run! (zk-test "3.4.5+dfsg-2")))))))
