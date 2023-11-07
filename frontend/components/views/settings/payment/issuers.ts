import {siAmericanexpress, siDinersclub, siDiscover, siMastercard, SimpleIcon, siVisa} from 'simple-icons'

export const ISSUERS: { [key: number]: {name: string, icon: SimpleIcon}} = {
  1: {name: 'Visa', icon: siVisa},
  2: {name: 'MasterCard', icon: siMastercard},
  3: {name: 'American Express', icon: siAmericanexpress},
  4: {name: 'Discover', icon: siDiscover},
  5: {name: "Diner's Club", icon: siDinersclub},
}
