// SPDX-License-Identifier: MIT
import './IVoteD21.sol';
pragma solidity >=0.4.22 <0.9.0;

contract D21 is IVoteD21 {
  address public owner;
  mapping(address => Subject) public subjects; 
  struct Voter{
      bool CanVote;
      int votesPositive;
      int votesNegative;
      mapping(address => bool) VotedSubjects;
  }
  address[] public userAddresses;
  mapping(address => Voter) public Voters;

  uint BlockCreated;

  constructor() {
        owner = msg.sender;
        BlockCreated = block.timestamp;
  }

  modifier CanVoteNeg(){ 
      require(Voters[msg.sender].votesPositive > 1, "U cannot vote negative when u didnt apply 2 positive votes yet -> see https://www.ih21.org/o-metode");
      _;
  }

  modifier isOutOfPositiveVotes(){ 
      require(Voters[msg.sender].votesPositive < 2, "U cannot vote because u had only 2 positives votes -> see https://www.ih21.org/o-metode");
      _;
  }

  modifier isOutOfNegativesVotes(){ 
      require(Voters[msg.sender].votesNegative < 1, "U cannot vote because u had only 1 negative vote -> see https://www.ih21.org/o-metode");
      _;
  }

  modifier isOwner() {
      require(msg.sender == owner, "U dont have permissions to use this function");
      _;
  }

  modifier isTimeOut(){
    require(block.timestamp - BlockCreated < 7 days, "Voting ended after 7 days from contract deployment");
      _;
  }

  modifier isVoter() {
      require(Voters[msg.sender].CanVote == true, "U are not in Voter list please contact the owner!");
      _;

  }

  modifier isSubjectAlreadyCreated(){
      require((keccak256(abi.encodePacked(subjects[msg.sender].name)) ==  keccak256(abi.encodePacked(''))), "You already created your subject!!");
      _;
  }

  function getSubject(address addr) external override view returns(Subject memory){
      return subjects[addr];
  }

  function addSubject(string memory name) external override isSubjectAlreadyCreated isTimeOut{
      subjects[msg.sender].name = name;
      userAddresses.push(msg.sender);
  }

  function getSubjects() external view override returns(address[] memory){
    return userAddresses;
  }

  function addVoter(address addr) external override isOwner isTimeOut{
      Voters[addr].CanVote = true;
  }

  function votePositive(address addr) external override isVoter isTimeOut isOutOfPositiveVotes {
      require(Voters[msg.sender].VotedSubjects[addr] != true, "U already voted for that subject!");
      Voters[msg.sender].votesPositive +=1;
      subjects[addr].votes += 1;
      Voters[msg.sender].VotedSubjects[addr] = true;
  }

  function voteNegative(address addr) external override isVoter isTimeOut CanVoteNeg isOutOfNegativesVotes{
    require(Voters[msg.sender].VotedSubjects[addr] != true, "U already voted for that subject!");
    Voters[msg.sender].votesNegative +=1;
    subjects[addr].votes -= 1;
    Voters[msg.sender].VotedSubjects[addr] = true;
  } 

  function getRemainingTime() external view override returns(uint){
    return (7 days) - (block.timestamp - BlockCreated); 
  }

}
