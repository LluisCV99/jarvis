import conf
import os
import shutil

TEST_CONF = "conf_test.json"
TEST_BACKUP = "conf_backup_test.json"

def setup_test_environment():
    shutil.copy("conf.json", TEST_CONF)

def teardown_test_environment():
    if os.path.exists(TEST_CONF):
        os.remove(TEST_CONF)
    if os.path.exists(TEST_BACKUP):
        os.remove(TEST_BACKUP)

def test_get_jarvis():
    print("Testing get_jarvis...")
    jarvis_conf = conf.get_jarvis(TEST_CONF)
    print(f"  -> Retrieved: Provider [{jarvis_conf.get('provider')}] | Model [{jarvis_conf.get('model')}]")
    assert jarvis_conf is not None
    assert "provider" in jarvis_conf
    assert "model" in jarvis_conf

def test_get_coder():
    print("Testing get_coder...")
    coder_conf = conf.get_coder(TEST_CONF)
    print(f"  -> Retrieved: Provider [{coder_conf.get('provider')}] | Model [{coder_conf.get('model')}]")
    assert coder_conf is not None
    assert "provider" in coder_conf
    assert "model" in coder_conf

def test_update_model():
    print("Testing update_model...")
    print("  -> Modifying Jarvis to: [test_provider] / [test_model_jarvis]")
    conf.update_model("jarvis", "test_provider", "test_model_jarvis", TEST_CONF)
    jarvis_conf = conf.get_jarvis(TEST_CONF)
    print(f"  -> Read after update: [{jarvis_conf['provider']}] / [{jarvis_conf['model']}]")
    assert jarvis_conf["provider"] == "test_provider"
    assert jarvis_conf["model"] == "test_model_jarvis"

    print("  -> Modifying Coder to: [test_provider] / [test_model_coder]")
    conf.update_model("coder", "test_provider", "test_model_coder", TEST_CONF)
    coder_conf = conf.get_coder(TEST_CONF)
    print(f"  -> Read after update: [{coder_conf['provider']}] / [{coder_conf['model']}]")
    assert coder_conf["provider"] == "test_provider"
    assert coder_conf["model"] == "test_model_coder"

def test_backup_and_restore():
    print("Testing backup and restore functionality...")
    conf.update_model("jarvis", "backup_provider", "backup_model", TEST_CONF)
    print("  -> Backing up state: [backup_provider] / [backup_model]")
    conf.create_backup(TEST_CONF, TEST_BACKUP)
    
    conf.update_model("jarvis", "error_provider", "error_model", TEST_CONF)
    print("  -> Modified or corrupted file: [error_provider] / [error_model]")
    
    conf.restore_backup(TEST_CONF, TEST_BACKUP)
    
    restored_conf = conf.get_jarvis(TEST_CONF)
    print(f"  -> Final state after restore: [{restored_conf['provider']}] / [{restored_conf['model']}]")
    
    assert restored_conf["provider"] == "backup_provider"
    assert restored_conf["model"] == "backup_model"

if __name__ == "__main__":
    print("Starting test suite...\n")
    print(">> Preparing test environment (temporary test files)...")
    setup_test_environment()
    print("-" * 50)
    
    tests_a_executar = [
        test_get_jarvis,
        test_get_coder,
        test_update_model,
        test_backup_and_restore
    ]
    
    tot_correcte = True
    
    try:
        for test in tests_a_executar:
            try:
                test()
                print("-" * 50)
            except AssertionError:
                print(f"\n❌ ERROR: Test '{test.__name__}' failed! Check the logic in 'conf.py'.")
                tot_correcte = False
                break
                
        if tot_correcte:
            print("\n✅ All tests passed successfully!")
            
    finally:
        print("\n>> Cleaning up: Deleting temporary test files...")
        teardown_test_environment()