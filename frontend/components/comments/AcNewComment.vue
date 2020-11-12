<template>
  <v-card :class="{comment: true, 'elevation-3': alternate}" class="new-comment" :color="color">
    <v-toolbar dense color="black" v-if="isRegistered || (isLoggedIn && guestOk)">
      <ac-avatar :user="viewer" :show-name="false" />
      <v-toolbar-title class="ml-1"><ac-link :to="profileLink(viewer)">{{viewerName}}</ac-link></v-toolbar-title><v-spacer />
    </v-toolbar>
    <v-card-text>
      <v-row no-gutters v-if="!isRegistered && !guestOk">
        <v-col class="text-center" cols="12" >
          <v-btn @click="editing=true" class="new-comment-button" :to="{name: 'Login', params: {tabName: 'login'}, query: {next: this.$route.fullPath}}">Log in or Register to
            Comment!
          </v-btn>
        </v-col>
      </v-row>
      <v-subheader v-else-if="!value">New Comment</v-subheader>
      <v-row no-gutters v-if="isRegistered || (isLoggedIn && guestOk)">
        <v-col cols="12" sm="12">
          <ac-form-container v-bind="newCommentForm.bind">
            <ac-form @submit.prevent="publish">
              <ac-bound-field :field="newCommentForm.fields.text" field-type="ac-editor">
                <v-col class="text-right" slot="actions">
                  <v-row dense>
                    <v-spacer />
                    <v-col class="shrink" v-if="value">
                      <v-tooltip top>
                        <template v-slot:activator="{ on }">
                          <v-btn v-on="on" @click="cancel" color="danger" fab small class="cancel-button">
                            <v-icon>cancel</v-icon>
                          </v-btn>
                        </template>
                        <span>Cancel</span>
                      </v-tooltip>
                    </v-col>
                    <v-col class="shrink" >
                    <v-tooltip top>
                      <template v-slot:activator="{ on }">
                        <v-btn v-on="on" color="blue" type="submit" fab class="submit-button" small>
                          <v-icon>send</v-icon>
                        </v-btn>
                      </template>
                      <span>Send</span>
                    </v-tooltip>
                    </v-col>
                  </v-row>
                </v-col>
              </ac-bound-field>
            </ac-form>
          </ac-form-container>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<style lang="stylus" scoped>
  .theme--dark .comment.alternate {
    background-color: var(--v-darkBase-darken2)
  }
</style>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Viewer from '../../mixins/viewer'
import AcEditor from '../fields/AcEditor.vue'
import {ListController} from '@/store/lists/controller'
import {Prop, Watch} from 'vue-property-decorator'
import AcAvatar from '@/components/AcAvatar.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import {FormController} from '@/store/forms/form-controller'
import AcBoundField from '@/components/fields/AcBoundField'
import {flatten, profileLink} from '@/lib/lib'
import AcForm from '@/components/wrappers/AcForm.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import Formatting from '@/mixins/formatting'
import {RawData} from '@/store/forms/types/RawData'

  @Component({
    components: {AcLink, AcForm, AcBoundField, AcFormContainer, AcAvatar, AcEditor},
  })
export default class AcNewComment extends mixins(Viewer, Formatting) {
    @Prop({required: true})
    public commentList!: ListController<Comment>

    @Prop({default: false})
    public alternate!: boolean

    @Prop({default: false})
    public value!: boolean

    @Prop({default: false})
    public guestOk!: boolean

    @Prop({default: () => ({})})
    public extraData!: RawData

    public newCommentForm: FormController = null as unknown as FormController

    public get color() {
      if (this.alternate) {
        // @ts-ignore
        return this.$vuetify.theme.currentTheme.darkBase.darken4
      }
    }

    // Used for when we're nested under a comment thread.
    public cancel() {
      this.$emit('input', false)
    }

    @Watch('extraData', {deep: true})
    public updateData() {
      this.newCommentForm.fields.extra_data.update(this.extraData)
    }

    public publish() {
      this.newCommentForm.submit().then(this.commentList.push).then(this.cancel).catch(this.newCommentForm.setErrors)
    }

    public created() {
      this.newCommentForm = this.$getForm(this.commentList.name + '_new', {
        endpoint: this.commentList.endpoint, fields: {text: {value: ''}, extra_data: {value: this.extraData}},
      })
    }
}
</script>
