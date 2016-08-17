(ns mmapd.core
    (:require [clojure.tools.logging :refer :all]
                          [jepsen [db    :as db]
                                               [control :as c]
                                               [tests :as tests]]
                          [jepsen.os.debian :as debian]))


(defn db
    "mmapd for a particular version."
    [version]
    (reify db/DB
          (setup! [_ test node]
                  (info node "installing mmapd" version)
                  (c/exec :wget :-O "/tmp/mmapd" "https://s3.amazonaws.com/mmapd-bin/mmapd"))

          (teardown! [_ test node]
                  (info node "tearing down mmapd"))))

(defn mmapd-test
    (info node "running mmapd-test" version)
    [version]
    (assoc tests/noop-test
                    :os debian/os
                    :db (db version)))

