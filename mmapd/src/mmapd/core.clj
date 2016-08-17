(ns mmapd.core
    (:require [clojure.tools.logging :refer :all]
                          [jepsen [db    :as db]
                                               [control :as c]
                                               [tests :as tests]]
                          [jepsen.os.debian :as debian]))


(defn db
    "Zookeeper DB for a particular version."
    [version]
    (reify db/DB
          (setup! [_ test node]
                  (info node "installing ZK" version)
                  (c/exec :wget :-O "/tmp/mmapd" "https://s3.amazonaws.com/mmapd-bin/mmapd"))

          (teardown! [_ test node]
                  (info node "tearing down ZK"))))

(defn zk-test
    [version]
    (assoc tests/noop-test
                    :os debian/os
                    :db (db version)))

