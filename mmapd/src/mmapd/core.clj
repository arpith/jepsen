(ns mmapd.core
    (:require [clojure.tools.logging :refer :all]
                          [jepsen [db    :as db]
                                               [control :as c]
                                               [tests :as tests]]
                          [jepsen.os.debian :as debian]))

(def binary "/usr/bin/mmapd")

(defn start-mmapd!
          [test node]
          (info node "starting mmapd")
          (c/exec :start-stop-daemon :--start
                  :--background
                  :--exec binary))

(defn db
    "mmapd for a particular version."
    [version]
    (reify db/DB
          (setup! [_ test node]
                  (info node "installing mmapd" version)
                  (c/exec :wget :-O binary "https://s3.amazonaws.com/mmapd-bin/mmapd")
                  (start-mmapd! test node))

          (teardown! [_ test node]
                  (info node "tearing down mmapd")
                  (c/exec :killall :-9 :mmapd))))

(defn mmapd-test
    [version]
    (assoc tests/noop-test
                    :os debian/os
                    :db (db version)))

