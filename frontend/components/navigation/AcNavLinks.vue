<template>
  <v-list dense style="min-height: 75vh">
    <v-list>
      <v-list-item @click="$emit('input', false)" :class="{'hidden-lg-and-up': !embedded}">
        <v-list-item-action>
          <v-icon>close</v-icon>
        </v-list-item-action>
        <v-list-item-title>Close Menu</v-list-item-title>
      </v-list-item>
      <v-list-item to="/" exact>
        <v-list-item-action>
          <v-icon>home</v-icon>
        </v-list-item-action>
        <v-list-item-title>Home</v-list-item-title>
      </v-list-item>
      <v-list-item v-if="!isRegistered" :to="{name: 'SessionSettings'}">
        <v-list-item-action>
          <v-icon>settings</v-icon>
        </v-list-item-action>
        <v-list-item-title>Settings</v-list-item-title>
      </v-list-item>
      <v-list-item :to="{name: 'Conversations', params: {username: subject.username}}" v-if="isRegistered">
        <v-list-item-action>
          <v-icon>email</v-icon>
        </v-list-item-action>
        <v-list-item-title>Private Messages</v-list-item-title>
      </v-list-item>
      <v-list-item :to="{name: 'CurrentOrders', params: {username: subject.username}}" v-if="isLoggedIn">
        <v-list-item-action>
          <v-icon>shopping_basket</v-icon>
        </v-list-item-action>
        <v-list-item-title>Orders</v-list-item-title>
      </v-list-item>
      <v-list-group
          no-action :value="true"
          sub-group
          v-if="isRegistered"
      >
        <template v-slot:activator>
          <v-list-item-title>Who's Open?</v-list-item-title>
        </template>
        <v-list-item :exact="true" :to="{name: 'SearchProducts'}" @click.capture.stop.prevent="searchOpen({})">
          <v-list-item-action class="who-is-open">
            <v-icon>location_city</v-icon>
          </v-list-item-action>
          <v-list-item-title>All Openings</v-list-item-title>
        </v-list-item>
        <v-list-item :exact="true" :to="{name: 'SearchProducts', query: {watch_list: 'true'}}" @click.capture.stop.prevent="searchOpen({watch_list: true})">
          <v-list-item-action class="who-is-open-watchlist">
            <v-icon>store</v-icon>
          </v-list-item-action>
          <v-list-item-title>Artists on my Watchlist</v-list-item-title>
        </v-list-item>
      </v-list-group>
      <v-list-item v-else :to="{name: 'SearchProducts'}" @click.capture.stop.prevent="searchOpen">
        <v-list-item-action class="who-is-open">
          <v-icon>store</v-icon>
        </v-list-item-action>
        <v-list-item-title>Who's Open?</v-list-item-title>
      </v-list-item>
      <v-list-group
          no-action
          :value="true"
          sub-group
          v-if="isRegistered"
      >
        <template v-slot:activator>
          <v-list-item-title>Recent Art</v-list-item-title>
        </template>
        <v-list-item :exact="true" :to="{name: 'SearchSubmissions'}" @click.capture.stop.prevent="searchSubmissions({})">
          <v-list-item-action class="recent-art">
            <v-icon>photo_library</v-icon>
          </v-list-item-action>
          <v-list-item-title>All Submissions</v-list-item-title>
        </v-list-item>
        <v-list-item :exact="true" :to="{name: 'SearchSubmissions', query: {watch_list: 'true'}}" @click.capture.stop.prevent="searchSubmissions({watch_list: true})">
          <v-list-item-action class="recent-art-watchlist">
            <v-icon>visibility</v-icon>
          </v-list-item-action>
          <v-list-item-title>Recent Art from Watchlist</v-list-item-title>
        </v-list-item>
      </v-list-group>
      <v-list-item v-else :to="{name: 'SearchSubmissions'}" @click.capture.stop.prevent="searchSubmissions({})">
        <v-list-item-action class="recent-art">
          <v-icon>photo_library</v-icon>
        </v-list-item-action>
        <v-list-item-title>Recent Art</v-list-item-title>
      </v-list-item>
      <v-list-item :to="{name: 'LinksAndStats', params: {username: subject.username}}" v-if="isRegistered">
        <v-list-item-action>
          <v-icon>star</v-icon>
        </v-list-item-action>
        <v-list-item-title>
          Referrals, Rewards, and Tools!
        </v-list-item-title>
      </v-list-item>
      <v-list-item :to="{name: 'Upgrade', params: {username: subject.username}}" v-if="isRegistered && !embedded">
        <v-list-item-action>
          <v-icon>arrow_upward</v-icon>
        </v-list-item-action>
        <v-list-item-title>
          Upgrade
        </v-list-item-title>
      </v-list-item>
      <v-list-item class="hidden-sm-and-up" v-if="!embedded && subject && subject.rating > 0">
        <ac-patch-field
            field-type="v-switch"
            :patcher="sfwMode"
            :save-indicator="false"
            label="SFW Mode"
        />
      </v-list-item>
    </v-list>
    <v-list v-if="isLoggedIn && subject.artist_mode">
      <v-divider/>
      <v-list-item :to="{name: 'Store', params: {username: subject.username}}">
        <v-list-item-action>
          <v-icon>storefront</v-icon>
        </v-list-item-action>
        <v-list-item-title>My Store</v-list-item-title>
      </v-list-item>
      <v-list-item :to="{name: 'CurrentSales', params: {username: subject.username}}">
        <v-list-item-action>
          <v-icon>monetization_on</v-icon>
        </v-list-item-action>
        <v-list-item-title>Sales/Invoicing</v-list-item-title>
      </v-list-item>
      <v-list-item :to="{name: 'Reports', params: {username: subject.username}}" v-if="isLoggedIn && (subject.artist_mode || subject.is_superuser)">
        <v-list-item-action>
          <v-icon>insert_chart</v-icon>
        </v-list-item-action>
        <v-list-item-title>Reports</v-list-item-title>
      </v-list-item>
      <v-list-item :to="{name: 'TableProducts'}" v-if="isLoggedIn && subject.is_staff">
        <v-list-item-action>
          <v-icon>{{storeCogPath}}</v-icon>
        </v-list-item-action>
        <v-list-item-title>Table Dashboard</v-list-item-title>
      </v-list-item>
      <v-divider />
    </v-list>
    <v-list v-if="isStaff">
      <v-list-item :to="{name: 'CurrentCases', params: {username: subject.username}}">
        <v-list-item-action>
          <v-icon>gavel</v-icon>
        </v-list-item-action>
        <v-list-item-title>Cases</v-list-item-title>
      </v-list-item>
    </v-list>
    <v-list-group :to="{name: 'Options', params: {'username': subject.username}}" v-if="isRegistered" prepend-icon="settings">
      <template v-slot:activator>
        <v-list-item-title>Settings</v-list-item-title>
      </template>
      <ac-setting-nav :username="subject.username" :nested="true" />
    </v-list-group>
    <v-list-item :to="{name: 'About'}" v-if="!embedded">
      <v-list-item-action>
        <v-icon>question_answer</v-icon>
      </v-list-item-action>
      <v-list-item-title>FAQ</v-list-item-title>
    </v-list-item>
    <v-list-item @click.prevent="logout()" v-if="isRegistered && !embedded">
      <v-list-item-action class="logout-button">
        <v-icon>exit_to_app</v-icon>
      </v-list-item-action>
      <v-list-item-title>Log out</v-list-item-title>
    </v-list-item>
    <v-list-item class="mt-3" :to="{name: 'Policies'}" v-if="!embedded">
      <v-list-item-action>
        <v-icon>info</v-icon>
      </v-list-item-action>
      <v-list-item-title>Privacy and Legal</v-list-item-title>
    </v-list-item>
  </v-list>
</template>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import {Prop} from 'vue-property-decorator'
import AcSettingNav from '@/components/navigation/AcSettingNav.vue'
import {FormController} from '@/store/forms/form-controller'
import {ProfileController} from '@/store/profiles/controller'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import {artCall, makeQueryParams} from '@/lib/lib'
import {mdiStoreCogOutline} from '@mdi/js'
import {RawData} from '@/store/forms/types/RawData'

@Component({
  components: {AcPatchField, AcSettingNav},
})
export default class AcNavDrawer extends Vue {
  public storeCogPath = mdiStoreCogOutline
  public searchForm: FormController = null as unknown as FormController
  @Prop({required: true})
  public value!: boolean

  @Prop({required: true})
  public subjectHandler!: ProfileController

  @Prop({required: true})
  public isRegistered!: boolean

  @Prop({required: true})
  public isLoggedIn!: boolean

  @Prop({default: false})
  public embedded!: boolean

  @Prop({required: true})
  public isStaff!: boolean

  @Prop({required: true})
  public isSuperuser!: boolean

  public get subject() {
    return this.subjectHandler.user.x
  }

  public get sfwMode() {
    return this.subjectHandler.user.patchers.sfw_mode
  }

  public searchOpen(data: RawData) {
    this.searchReplace(data)
    this.$router.push({name: 'SearchProducts', query: makeQueryParams(this.searchForm.rawData)})
  }

  public searchReplace(data: RawData) {
    this.searchForm.reset()
    for (const key of Object.keys(data)) {
      this.searchForm.fields[key].update(data[key])
    }
  }

  public searchSubmissions(data: RawData) {
    this.searchReplace(data)
    this.$router.push({name: 'SearchSubmissions', query: makeQueryParams(this.searchForm.rawData)})
  }

  public logout() {
    artCall({
      url: '/api/profiles/logout/',
      method: 'post',
    }).then(this.subjectHandler.user.setX).then(() => {
      this.$router.push({name: 'Home'})
      this.$emit('input', null)
    })
  }

  public created() {
    this.searchForm = this.$getForm('search')
  }
}
</script>
