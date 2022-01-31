import pytest
import brownie

from brownie import chain

@pytest.fixture
def SystemD21(D21, accounts):
    # initialize contract from the first account
    contract = D21.deploy({'from': accounts[0]})
    return contract

# persistent contract after deadline (expired)
@pytest.fixture(scope="module")
def SystemD21Ended(D21,accounts):
    contract = D21.deploy({'from': accounts[0]}) 
    contract.addSubject("SPOLU", {'from': accounts[0]})
    contract.addVoter(accounts[1], {'from': accounts[0]})    
    chain.sleep(605000)
    chain.mine
    return contract


# Owner 
def test_checkCorrectOwner(SystemD21, accounts):
    assert SystemD21.owner() == accounts[0]


# Add voter
def test_addVoterAsOwner(SystemD21, accounts):
    SystemD21.addVoter(accounts[1], {'from': accounts[0]})
    assert SystemD21.Voters(accounts[1])[0] == True


def test_addVoterAsNotOwner(SystemD21, accounts):
    with brownie.reverts("U dont have permissions to use this function"):
        SystemD21.addVoter(accounts[2], {'from': accounts[1]})

    assert SystemD21.Voters(accounts[2])[0] == False


# Add subject
def test_addSubject(SystemD21, accounts):
    SystemD21.addSubject("ANO", {'from': accounts[0]})
    SystemD21.addSubject("SPOLU", {'from': accounts[1]})

    assert SystemD21.getSubject(accounts[0])[0] == "ANO" and SystemD21.getSubject(accounts[0])[1] == 0
    assert SystemD21.getSubject(accounts[1])[0] == "SPOLU" and SystemD21.getSubject(accounts[1])[1] == 0
    assert accounts[0] in SystemD21.getSubjects() and accounts[1] in SystemD21.getSubjects()


def test_addTwoSubjectsFromTheSameAddress(SystemD21, accounts):
    SystemD21.addSubject("ANO", {'from': accounts[1]})

    with brownie.reverts("You already created your subject!!"):
        SystemD21.addSubject("SPOLU", {'from': accounts[1]})

    assert SystemD21.getSubject(accounts[1])[0] == "ANO" and SystemD21.getSubject(accounts[1])[1] == 0


# ISSUE M3 - not handled input "Name" in contract
def test_addSubjectBlankName(SystemD21, accounts):
    SystemD21.addSubject("", {'from': accounts[1]})

    with pytest.raises(AssertionError):
        assert accounts[1] not in SystemD21.getSubjects()


# ISSUE M4 - not handled adding already existing subject
def test_addExistingSubject(SystemD21, accounts):
    SystemD21.addSubject("SPOLU", {'from': accounts[0]})
    SystemD21.addSubject("SPOLU", {'from': accounts[1]})

    with pytest.raises(AssertionError):
        assert accounts[0] in SystemD21.getSubjects() and SystemD21.getSubject(accounts[0])[0] == "SPOLU"
        assert accounts[1] not in SystemD21.getSubjects() 

# Get subject
def test_getRegisteredSubject(SystemD21, accounts):
    SystemD21.addSubject("ANO", {'from': accounts[1]})
    assert accounts[1] in SystemD21.getSubjects()
    assert SystemD21.getSubject(accounts[1])[0] == "ANO"


def test_getNotRegisteredSubject(SystemD21, accounts):
    with pytest.raises(AssertionError):
        assert accounts[1] in SystemD21.getSubjects()
    


# Get subjects
def test_getSubjects(SystemD21, accounts):
    SystemD21.addSubject("ANO", {'from': accounts[0]})
    SystemD21.addSubject("SPOLU", {'from': accounts[1]})
    SystemD21.addSubject("SPD", {'from': accounts[2]})

    addresses = SystemD21.getSubjects()
    assert len(addresses) == 3
    assert accounts[0] in SystemD21.getSubjects()
    assert accounts[1] in SystemD21.getSubjects()
    assert accounts[2] in SystemD21.getSubjects()


def test_getSubjectsWithoutRegistered(SystemD21, accounts):
    addresses = SystemD21.getSubjects()
    assert len(addresses) == 0


# Vote positive
def test_votePositiveWithoutPermission(SystemD21, accounts):
    SystemD21.addSubject("ANO", {'from': accounts[0]})

    with brownie.reverts("U are not in Voter list please contact the owner!"):
        SystemD21.votePositive(accounts[0], {'from': accounts[1]})

    assert SystemD21.Voters(accounts[1])[1] == 0
    assert SystemD21.subjects(accounts[0])[1] == 0


def test_votePositiveOnce(SystemD21, accounts):
    assert SystemD21.Voters(accounts[1])[1] == 0
    assert SystemD21.subjects(accounts[0])[1] == 0
    SystemD21.addSubject("ANO", {'from': accounts[0]})
    SystemD21.addVoter(accounts[1], {'from': accounts[0]})

    SystemD21.votePositive(accounts[0], {'from': accounts[1]})
    assert SystemD21.Voters(accounts[1])[1] == 1
    assert SystemD21.subjects(accounts[0])[1] == 1


def test_votePositiveTwice(SystemD21, accounts):
    assert SystemD21.Voters(accounts[1])[1] == 0

    SystemD21.addSubject("ANO", {'from': accounts[0]})
    SystemD21.addSubject("SPOLU", {'from': accounts[1]})

    SystemD21.addVoter(accounts[1], {'from': accounts[0]})

    SystemD21.votePositive(accounts[0], {'from': accounts[1]})
    SystemD21.votePositive(accounts[1], {'from': accounts[1]})

    assert SystemD21.Voters(accounts[1])[1] == 2
    assert SystemD21.subjects(accounts[0])[1] == 1
    assert SystemD21.subjects(accounts[1])[1] == 1


def test_votePositiveTwiceForTheSameSubject(SystemD21, accounts):
    SystemD21.addSubject("ANO", {'from': accounts[0]})
    SystemD21.addVoter(accounts[1], {'from': accounts[0]})

    SystemD21.votePositive(accounts[0], {'from': accounts[1]})

    with brownie.reverts("U already voted for that subject!"):
        SystemD21.votePositive(accounts[0], {'from': accounts[1]})


def test_votePositiveThreeTimes(SystemD21, accounts):
    SystemD21.addSubject("ANO", {'from': accounts[0]})
    SystemD21.addSubject("SPOLU", {'from': accounts[1]})
    SystemD21.addSubject("SPD", {'from': accounts[2]})

    SystemD21.addVoter(accounts[1], {'from': accounts[0]})

    SystemD21.votePositive(accounts[0], {'from': accounts[1]})
    SystemD21.votePositive(accounts[1], {'from': accounts[1]})

    with brownie.reverts("U cannot vote because u had only 2 positives votes -> see https://www.ih21.org/o-metode"):
        SystemD21.votePositive(accounts[2], {'from': accounts[1]})


# ISSUE M5 - unhandled error in contract - vote for subject before its creation
def test_votePositiveNotRegisteredSubject(SystemD21, accounts):
    SystemD21.addVoter(accounts[1], {'from': accounts[0]})
    SystemD21.votePositive(accounts[0], {'from': accounts[1]})

    with pytest.raises(AssertionError):
        assert SystemD21.subjects(accounts[0])[1] == 1 and SystemD21.subjects(accounts[0])[0] != ''


# Vote negative
def test_voteNegativeAfterNonePositive(SystemD21, accounts):
    assert SystemD21.Voters(accounts[1])[1] == 0
    assert SystemD21.Voters(accounts[1])[2] == 0
    assert SystemD21.subjects(accounts[0])[1] == 0

    SystemD21.addSubject("ANO", {'from': accounts[0]})
    SystemD21.addVoter(accounts[1], {'from': accounts[0]})

    with brownie.reverts("U cannot vote negative when u didnt apply 2 positive votes yet -> see https://www.ih21.org/o-metode"):
        SystemD21.voteNegative(accounts[0], {'from': accounts[1]})

    assert SystemD21.Voters(accounts[1])[1] == 0
    assert SystemD21.Voters(accounts[1])[2] == 0
    assert SystemD21.subjects(accounts[0])[1] == 0


def test_voteNegativeAfterOnePositive(SystemD21, accounts):
    SystemD21.addSubject("ANO", {'from': accounts[0]})
    SystemD21.addSubject("SPOLU", {'from': accounts[1]})
    SystemD21.addVoter(accounts[1], {'from': accounts[0]})

    SystemD21.votePositive(accounts[0], {'from': accounts[1]})
    assert SystemD21.Voters(accounts[1])[1] == 1
    assert SystemD21.Voters(accounts[1])[2] == 0
    assert SystemD21.subjects(accounts[0])[1] == 1

    with brownie.reverts("U cannot vote negative when u didnt apply 2 positive votes yet -> see https://www.ih21.org/o-metode"):
        SystemD21.voteNegative(accounts[1], {'from': accounts[1]})
    assert SystemD21.Voters(accounts[1])[1] == 1
    assert SystemD21.Voters(accounts[1])[2] == 0
    assert SystemD21.subjects(accounts[0])[1] == 1


def test_voteNegativeAfterTwoPositive(SystemD21, accounts):
    SystemD21.addSubject("ANO", {'from': accounts[0]})
    SystemD21.addSubject("SPOLU", {'from': accounts[1]})
    SystemD21.addSubject("SPD", {'from': accounts[2]})
    SystemD21.addVoter(accounts[1], {'from': accounts[0]})

    SystemD21.votePositive(accounts[0], {'from': accounts[1]})
    SystemD21.votePositive(accounts[1], {'from': accounts[1]})
    assert SystemD21.Voters(accounts[1])[1] == 2
    assert SystemD21.Voters(accounts[1])[2] == 0
    assert SystemD21.subjects(accounts[1])[1] == 1

    SystemD21.voteNegative(accounts[2], {'from': accounts[1]})
    assert SystemD21.Voters(accounts[1])[1] == 2
    assert SystemD21.Voters(accounts[1])[2] == 1
    assert SystemD21.subjects(accounts[2])[1] == -1


def test_voteNegativeAfterTwoPositiveAndOneNegative(SystemD21, accounts):
    SystemD21.addSubject("ANO", {'from': accounts[0]})
    SystemD21.addSubject("SPOLU", {'from': accounts[1]})
    SystemD21.addSubject("SPD", {'from': accounts[2]})
    SystemD21.addSubject("Pirati", {'from': accounts[3]})
    SystemD21.addVoter(accounts[1], {'from': accounts[0]})

    SystemD21.votePositive(accounts[0], {'from': accounts[1]})
    SystemD21.votePositive(accounts[1], {'from': accounts[1]})
    SystemD21.voteNegative(accounts[2], {'from': accounts[1]})

    with brownie.reverts("U cannot vote because u had only 1 negative vote -> see https://www.ih21.org/o-metode"):
        SystemD21.voteNegative(accounts[3], {'from': accounts[1]})

    assert SystemD21.Voters(accounts[1])[1] == 2
    assert SystemD21.Voters(accounts[1])[2] == 1
    assert SystemD21.subjects(accounts[3])[1] == 0


def test_voteNegativeAfterPositiveForTheSameSubject(SystemD21, accounts):
    SystemD21.addSubject("ANO", {'from': accounts[0]})
    SystemD21.addSubject("SPOLU", {'from': accounts[1]})
    SystemD21.addSubject("SPD", {'from': accounts[2]})

    SystemD21.addVoter(accounts[1], {'from': accounts[0]})

    SystemD21.votePositive(accounts[0], {'from': accounts[1]})
    SystemD21.votePositive(accounts[1], {'from': accounts[1]})

    with brownie.reverts("U already voted for that subject!"):
        SystemD21.voteNegative(accounts[1], {'from': accounts[1]})


# Get remaining time 
def test_getRemainingTime(SystemD21, accounts):
    assert SystemD21.getRemainingTime({'from': accounts[0]}) <= 604800 and SystemD21.getRemainingTime({'from': accounts[0]}) > 0


# call functions after deadline
def test_AddSubjectAfterDeadline(SystemD21Ended, accounts):
    with brownie.reverts("Voting ended after 7 days from contract deployment"):
        SystemD21Ended.addSubject("Pirati", {'from': accounts[1]})

def test_AddVoterAfterDeadline(SystemD21Ended, accounts):
    with brownie.reverts("Voting ended after 7 days from contract deployment"):
        SystemD21Ended.addVoter(accounts[2], {'from': accounts[0]})  

def test_votePositiveAfterDeadline(SystemD21Ended, accounts):
    with brownie.reverts("Voting ended after 7 days from contract deployment"):
        SystemD21Ended.votePositive(accounts[0], {'from': accounts[1]})

def test_voteNegativeAfterDeadline(SystemD21Ended, accounts):
    with brownie.reverts("Voting ended after 7 days from contract deployment"):
        SystemD21Ended.voteNegative(accounts[0], {'from': accounts[1]})

