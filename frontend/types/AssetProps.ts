//   @Prop({default: false})
//   public compact!: boolean
//
//   @Prop({default: false})
//   public terse!: boolean
//
//   @Prop({default: false})
//   public popOut!: boolean
//
//   @Prop()
//   public contain!: string
//
//   @Prop({default: '/static/images/default-avatar.png'})
//   public fallbackImage!: string
export default interface AssetProps {
  compact?: boolean,
  terse?: boolean,
  contain?: boolean,
  popOut?: boolean,
  fallbackImage?: string,
}
