pragma solidity >=0.4.22 <0.9.0;

interface IVoteD21{

  struct Subject{
      string name;
      int votes;
  }
    function addSubject(string memory name) external;
    function getSubject(address addr) external view returns(Subject memory);
    function getSubjects() external view returns(address[] memory);
    function addVoter(address addr) external;
    function votePositive(address addr) external;
    function voteNegative(address addr) external;
    function getRemainingTime() external view returns(uint);

}